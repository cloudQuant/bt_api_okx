#!/usr/bin/env python3
"""把 OKX mixins 的机械切分文件（``*_partN``）合并回单一逻辑模块。

背景：这些 mixin 原是按行数机械切分的（``account_mixin_part1/2`` 等），
切分边界与职责无关、命名两套约定，导致 43 个文件里 25 个是 part 文件。
本脚本把每个逻辑模块的 Part 类方法合并进聚合类，产出单一模块并删除 part 文件。

安全性依据（已在合并前核实）：
  · 方法名无重复（否则会静默覆盖）；
  · Part 类内无 ``super()`` 调用、无 ``__init__``、无类属性/注解
    → 合并与方法顺序无关，MRO 变化不影响语义；
  · mixins 之外仅 1 处引用 Part 类（某测试），由调用方负责改为聚合类。

用法：
    python merge_mixin_parts.py --check          # 只报告将要合并的分组
    python merge_mixin_parts.py --group account_mixin.py
    python merge_mixin_parts.py --all
"""

from __future__ import annotations

import argparse
import ast
import re
from dataclasses import dataclass
from pathlib import Path

MIXINS_DIR = (
    Path(__file__).resolve().parent.parent
    / "src"
    / "bt_api_okx"
    / "feeds"
    / "live_okx"
    / "mixins"
)


@dataclass
class Group:
    aggregate: Path
    parts: list[Path]
    class_name: str


def _module_parts(path: Path) -> tuple[str | None, list[str], list[str], dict[str, list[str]]]:
    """返回 (docstring, 头部import源码行, 其他顶层语句源码行, {类名: 方法源码片段})。"""
    src = path.read_text(encoding="utf-8")
    lines = src.splitlines(keepends=True)
    tree = ast.parse(src)

    docstring = ast.get_docstring(tree, clean=False)
    imports: list[str] = []
    others: list[str] = []
    classes: dict[str, list[str]] = {}

    def slice_from(node: ast.stmt) -> str:
        start = node.lineno
        for deco in getattr(node, "decorator_list", []) or []:
            start = min(start, deco.lineno)
        return "".join(lines[start - 1 : node.end_lineno])

    for node in tree.body:
        if isinstance(node, (ast.Import, ast.ImportFrom)):
            imports.append(slice_from(node))
        elif isinstance(node, ast.ClassDef):
            body_items: list[str] = []
            for item in node.body:
                if isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    body_items.append(slice_from(item))
                elif isinstance(item, (ast.Assign, ast.AnnAssign)):
                    # 类属性/注解：按原顺序保留（合并时一并搬入新类体）
                    body_items.append(slice_from(item))
                elif isinstance(item, ast.Expr) and isinstance(item.value, ast.Constant):
                    continue  # 类自身的 docstring 丢弃，合并时统一生成
                elif isinstance(item, ast.Pass):
                    continue
                else:
                    raise SystemExit(f"{path}: 类 {node.name} 含未预期语句 {type(item).__name__}")
            classes[node.name] = body_items
        elif isinstance(node, ast.Expr) and isinstance(node.value, ast.Constant):
            continue  # 模块 docstring
        else:
            others.append(slice_from(node))

    return docstring, imports, others, classes


def discover_groups() -> list[Group]:
    groups: list[Group] = []
    for agg in sorted(MIXINS_DIR.glob("*_mixin.py")):
        _, imports, _, classes = _module_parts(agg)
        part_names: list[str] = []
        for imp in imports:
            m = re.search(r"import\s+(\w*Part\w*)", imp)
            if m:
                part_names.append(m.group(1))
        if not part_names:
            continue
        # 聚合类名：本文件定义的类
        agg_class = next(iter(classes), None)
        if agg_class is None:
            continue
        parts: list[Path] = []
        for name in part_names:
            matches = [p for p in MIXINS_DIR.glob("*.py") if f"class {name}" in p.read_text(encoding="utf-8")]
            if not matches:
                raise SystemExit(f"找不到 Part 类 {name} 的文件")
            parts.append(matches[0])
        groups.append(Group(aggregate=agg, parts=parts, class_name=agg_class))
    return groups


def merge(group: Group) -> None:
    agg_doc, agg_imports, agg_others, agg_classes = _module_parts(group.aggregate)
    title = group.class_name

    imports: list[str] = [imp for imp in agg_imports if not re.search(r"import\s+\w*Part\w*", imp)]
    import_lines: list[str] = []
    methods: list[str] = []
    others: list[str] = list(agg_others)

    for part in group.parts:
        _, p_imports, p_others, p_classes = _module_parts(part)
        imports.extend(p_imports)
        others.extend(p_others)
        for methods_list in p_classes.values():
            methods.extend(methods_list)

    # 去重 import（保留首次出现），后续交给 ruff --fix 排序与清理未用项
    seen: set[str] = set()
    for imp in imports:
        key = imp.strip()
        if key not in seen:
            seen.add(key)
            import_lines.append(imp)

    body: list[str] = []
    body.append(f'"""\nOKX API - {title}\n\n由机械切分的 ``*_partN`` 模块合并而来（迭代07 结构治理）。\n"""\n')
    body.append("\nfrom __future__ import annotations\n\n")
    body.extend(import_lines)
    body.append("\n\n")
    body.extend(others)
    if others:
        body.append("\n\n")
    body.append(f'class {group.class_name}:\n    """{group.class_name} 方法集合（OKX REST 端点）。"""\n')
    for chunk in methods:
        # 方法源码已含类体缩进（取自原 Part 类体），直接写入，切勿再次缩进
        body.append(chunk if chunk.endswith("\n") else chunk + "\n")
        body.append("\n")

    group.aggregate.write_text("".join(body), encoding="utf-8")
    for part in group.parts:
        part.unlink()
    print(f"  合并 {group.class_name:24s} ← {len(group.parts)} 个 part 文件，方法 {len(methods)} 个")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--group", default=None, help="只处理某个聚合文件（如 account_mixin.py）")
    parser.add_argument("--all", action="store_true")
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()

    groups = discover_groups()
    if args.check:
        for g in groups:
            print(f"{g.aggregate.name:32s} ← {[p.name for p in g.parts]}")
        return 0

    if args.group:
        groups = [g for g in groups if g.aggregate.name == args.group]
        if not groups:
            raise SystemExit(f"未找到分组: {args.group}")
    elif not args.all:
        raise SystemExit("请指定 --group <name> 或 --all（或 --check）")

    for g in groups:
        merge(g)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
