"""把 OKX mixins 里逐端点手写的三段样板收敛为统一委托调用。

历史形态：每个端点 3 个方法（builder + 同步包装 + 异步包装），约 39 行里约 35 行是样板:

    def _get_currencies(self, ccy=None, extra_data=None, **kwargs):
        # docstring + request_type 赋值 + params 组装
        # path / update_extra_data / kwargs 合并 / return 三元组   <-- 三个方法都重复这套

收敛后：builder 只保留 params 组装并委托 _finish；两个包装方法各一行委托
_rest / _rest_async。签名与文档串保持不变，因此调用方与测试无需改动。

只改**严格匹配模板**的方法：凡形态不同的端点一律跳过并计数，交人工处理，
脚本不会去"猜"语义不同的实现。

用法:
    python scripts/collapse_endpoints.py --dry-run
    python scripts/collapse_endpoints.py --apply
"""

from __future__ import annotations

import argparse
import ast
import re
import sys
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

# 构造方法尾部（5 个固定键 + kwargs 合并 + 返回三元组）
BUILDER_TAIL = re.compile(
    r"(?P<indent>[ \t]*)path = self\._params\.get_rest_path\(request_type\)\n"
    r"[ \t]*extra_data = update_extra_data\(\n"
    r"[ \t]*extra_data,\n"
    r"[ \t]*\*\*\{\n"
    r'[ \t]*"request_type": request_type,\n'
    r'[ \t]*"symbol_name": (?P<symbol>.+?),\n'
    r'[ \t]*"asset_type": self\.asset_type,\n'
    r'[ \t]*"exchange_name": self\.exchange_name,\n'
    r'[ \t]*"normalize_function": (?P<norm>.+?),\n'
    r"[ \t]*\},\n"
    r"[ \t]*\)\n"
    r"[ \t]*if kwargs is not None:\n"
    r"[ \t]*extra_data\.update\(kwargs\)\n"
    r"[ \t]*return path, params, extra_data\n"
)

REQUEST_TYPE_LINE = re.compile(r'^[ \t]*request_type = "(?P<value>[^"]+)"\n', re.M)

# 同步包装方法体
SYNC_BODY = re.compile(
    r"(?P<indent>[ \t]*)path, params, extra_data = self\.(?P<builder>_\w+)\((?P<args>[^\n]*)\)\n"
    r"[ \t]*data = self\.request\(path, params=params, extra_data=extra_data\)\n"
    r"[ \t]*return data\n"
)

# 异步包装方法体
ASYNC_BODY = re.compile(
    r"(?P<indent>[ \t]*)path, params, extra_data = self\.(?P<builder>_\w+)\((?P<args>[^\n]*)\)\n"
    r"[ \t]*self\.submit\(\n"
    r"[ \t]*self\.async_request\(path, params=params, extra_data=extra_data\),\n"
    r"[ \t]*callback=self\.async_callback,\n"
    r"[ \t]*\)\n"
)


@dataclass
class Stats:
    builders_done: int = 0
    builders_skipped: list[str] = None  # type: ignore[assignment]
    sync_done: int = 0
    async_done: int = 0
    sync_skipped: int = 0
    async_skipped: int = 0

    def __post_init__(self) -> None:
        if self.builders_skipped is None:
            self.builders_skipped = []


def _method_spans(tree: ast.Module, src_lines: list[str]) -> list[tuple[ast.AST, str, int, int]]:
    """返回 [(AST 节点, 方法名, 起行, 止行)]（1-based，含装饰器）。"""
    spans = []
    for node in ast.walk(tree):
        if not isinstance(node, ast.ClassDef):
            continue
        for item in node.body:
            if isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef)):
                start = item.lineno
                for deco in item.decorator_list:
                    start = min(start, deco.lineno)
                spans.append((item, item.name, start, item.end_lineno))
    return spans


def _docstring_end_line(node: ast.AST) -> int | None:
    body = getattr(node, "body", None)
    if body and isinstance(body[0], ast.Expr) and isinstance(body[0].value, ast.Constant) \
            and isinstance(body[0].value.value, str):
        return body[0].end_lineno
    return None


def _body_start_offset(node: ast.AST, lines: list[str], start_line: int) -> int:
    """方法体（跳过 docstring）在方法源码串中的字符偏移。"""
    doc_end = _docstring_end_line(node)
    first_body_line = (doc_end + 1) if doc_end else node.body[0].lineno  # type: ignore[attr-defined]
    return len("".join(lines[start_line - 1 : first_body_line - 1]))


def _is_canonical_request_call(call: ast.Call, func_name: str) -> bool:
    """内层调用必须恰好是 ``<func_name>(path, params=params, extra_data=extra_data)``。

    历史实现里有少数端点写成 ``async_request(path, **extra_data)`` 等变体
    （把参数以展开方式传入），形态不同即语义不同——必须跳过，不能"顺手统一"。
    """
    if ast.unparse(call.func) != func_name:
        return False
    if len(call.args) != 1 or ast.unparse(call.args[0]) != "path":
        return False
    if {kw.arg for kw in call.keywords} != {"params", "extra_data"}:
        return False
    return all(ast.unparse(kw.value) == kw.arg for kw in call.keywords)


def _classify_wrapper(node: ast.AST, src: str, method_src: str) -> tuple[str, str, bool] | None:
    """识别标准包装形态，返回 (builder 名, 参数字符串, 是否异步)；否则 None。"""
    body = list(node.body)  # type: ignore[attr-defined]
    if body and isinstance(body[0], ast.Expr) and isinstance(body[0].value, ast.Constant) \
            and isinstance(body[0].value.value, str):
        body = body[1:]
    # 同步包装：3 句（builder 调用 / self.request / return data）
    # 异步包装：2 句（builder 调用 / self.submit(...)）
    if len(body) not in (2, 3):
        return None
    first, second = body[0], body[1]
    # 第一句：path, params, extra_data = self._<builder>(...)
    if not (isinstance(first, ast.Assign) and len(first.targets) == 1
            and isinstance(first.targets[0], ast.Tuple) and isinstance(first.value, ast.Call)):
        return None
    call = first.value
    func_src = ast.unparse(call.func)
    if not func_src.startswith("self._"):
        return None
    builder = func_src[len("self._"):]
    call_src = ast.get_source_segment(src, call) or ""
    if "(" not in call_src:
        return None
    args_src = call_src[call_src.index("(") + 1 : call_src.rindex(")")].strip()
    args_src = re.sub(r"\s+", " ", args_src)
    # 第二句：同步 self.request(...) 或异步 self.submit(self.async_request(...))
    if isinstance(second, ast.Assign) and isinstance(second.value, ast.Call) \
            and _is_canonical_request_call(second.value, "self.request"):
        return builder, args_src, False
    if isinstance(second, ast.Expr) and isinstance(second.value, ast.Call):
        submit = second.value
        if ast.unparse(submit.func) != "self.submit":
            return None
        if {kw.arg for kw in submit.keywords} != {"callback"}:
            return None
        if not submit.args or not isinstance(submit.args[0], ast.Call):
            return None
        if not _is_canonical_request_call(submit.args[0], "self.async_request"):
            return None
        return builder, args_src, True
    return None


def collapse_module(path: Path, apply: bool) -> Stats:
    src = path.read_text(encoding="utf-8")
    lines = src.splitlines(keepends=True)
    tree = ast.parse(src)
    stats = Stats()
    edits: list[tuple[int, int, str]] = []  # (start_idx, end_idx_exclusive, new_text)

    for node, name, start, end in _method_spans(tree, lines):
        method_src = "".join(lines[start - 1 : end])
        offset = start - 1

        m = BUILDER_TAIL.search(method_src)
        if m and name.startswith("_") and not name.endswith("_normalize_function"):
            rt = REQUEST_TYPE_LINE.search(method_src)
            if not rt:
                stats.builders_skipped.append(f"{path.name}:{name} (缺 request_type 字面量)")
                continue
            request_type = rt.group("value")
            prefix = method_src[: m.start()]
            suffix = method_src[m.end() :]
            # request_type 若不再被使用，删掉其赋值行（避免 F841）
            if (prefix + suffix).count("request_type") == 1:  # 只剩赋值那一处
                rt2 = REQUEST_TYPE_LINE.search(prefix)
                if rt2:
                    prefix = prefix[: rt2.start()] + prefix[rt2.end() :]
            indent = m.group("indent")
            call = (
                f'{indent}return self._finish(\n'
                f'{indent}    "{request_type}",\n'
                f"{indent}    params,\n"
                f"{indent}    extra_data,\n"
                f'{indent}    {m.group("symbol").strip()},\n'
                f'{indent}    {m.group("norm").strip()},\n'
                f"{indent}    kwargs,\n"
                f"{indent})\n"
            )
            new_method = prefix + call + suffix
            edits.append((offset, offset + len(lines[start - 1 : end]), new_method))
            stats.builders_done += 1
            continue

        # 同步/异步包装：用 AST 判定形态（对多行调用免疫），支持多行参数
        wrapper = _classify_wrapper(node, src, method_src)
        if wrapper is not None:
            builder, args_src, is_async = wrapper
            indent = " " * (len(method_src) - len(method_src.lstrip(" \t")) + 4)
            helper = "_rest_async" if is_async else "_rest"
            call = f'{indent}return self.{helper}("{builder}", {args_src})\n' if args_src else f'{indent}return self.{helper}("{builder}")\n'
            body_start = _body_start_offset(node, lines, start)
            # body_start 已是相对 method_src 的偏移，切勿再减绝对行号
            edits.append((offset, offset + len(lines[start - 1 : end]), method_src[:body_start] + call))
            if is_async:
                stats.async_done += 1
            else:
                stats.sync_done += 1
            continue

        if name.startswith("async_"):
            stats.async_skipped += 1
        elif not name.startswith("_"):
            stats.sync_skipped += 1

    if apply and edits:
        new_lines = list(lines)
        for start_idx, end_idx, text in sorted(edits, key=lambda e: -e[0]):
            new_lines[start_idx:end_idx] = [text]
        new_src = "".join(new_lines)
        ast.parse(new_src)  # 语法自检：不合法则抛错，不落盘
        path.write_text(new_src, encoding="utf-8")
    return stats


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--apply", action="store_true")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()
    if not (args.apply or args.dry_run):
        parser.error("请指定 --dry-run 或 --apply")

    totals = Stats()
    for path in sorted(MIXINS_DIR.glob("*.py")):
        if path.name in ("__init__.py", "rest_call_mixin.py"):
            continue
        s = collapse_module(path, apply=args.apply)
        if s.builders_done or s.sync_done or s.async_done:
            print(
                f"{path.name:32s} builder {s.builders_done:3d} | sync {s.sync_done:3d} | "
                f"async {s.async_done:3d} | 跳过 sync {s.sync_skipped} / async {s.async_skipped}"
            )
        totals.builders_done += s.builders_done
        totals.sync_done += s.sync_done
        totals.async_done += s.async_done
        totals.sync_skipped += s.sync_skipped
        totals.async_skipped += s.async_skipped
        totals.builders_skipped.extend(s.builders_skipped)

    print(
        f"\n合计：builder {totals.builders_done} | sync {totals.sync_done} | async {totals.async_done}"
        f" | 模式不匹配的 sync {totals.sync_skipped} / async {totals.async_skipped}"
    )
    if totals.builders_skipped:
        print(f"未收敛的 builder（{len(totals.builders_skipped)} 个，需人工）：")
        for item in totals.builders_skipped[:15]:
            print("  ", item)
    return 0


if __name__ == "__main__":
    sys.exit(main())
