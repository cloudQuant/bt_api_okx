"""REST 端点调用的统一实现，供各 mixin 复用。

历史形态：每个端点手写三个方法——``_ep`` 构造 ``(path, params, extra_data)``、
``ep`` 同步调用 ``request``、``async_ep`` 异步 ``submit``。三者高度重复，
全目录因此膨胀出约 1 万行样板。

现在把"每家端点都一样的部分"收敛到这里：

* :meth:`_finish` —— 补齐 ``path`` 与 ``extra_data`` 元信息，返回三元组；
* :meth:`_rest` —— 调 builder 后走同步 ``request``；
* :meth:`_rest_async` —— 调 builder 后走异步 ``submit``。

各端点仍保留**显式方法与真实签名**（测试会直接调用 builder 与
``*_normalize_function``，且显式签名便于断点与静态分析），只是方法体变为一行委托。

这里刻意不用 ``__getattr__``/``exec`` 动态生成方法：那会破坏
``inspect.signature``、回溯定位与 IDE 跳转，收益却不比本方案更多。
"""

from __future__ import annotations

from typing import Any

from bt_api_base.functions.utils import update_extra_data

__all__ = ["RestCallMixin"]


class RestCallMixin:
    """所有 OKX mixin 的公共基类：REST 调用的重复部分。"""

    # 宿主（OkxRequestData 及其基类）提供的属性/方法；用注解声明以便类型检查。
    asset_type: Any
    exchange_name: Any
    _params: Any

    def _finish(
        self,
        request_type: str,
        params: dict[str, Any],
        extra_data: Any,
        symbol_name: Any,
        normalize_function: Any,
        kwargs: dict[str, Any],
    ) -> tuple[str, dict[str, Any], dict[str, Any]]:
        """补齐请求路径与 ``extra_data`` 元信息，返回 ``(path, params, extra_data)``。

        与历史实现逐行等价：``request_type`` / ``symbol_name`` / ``asset_type`` /
        ``exchange_name`` / ``normalize_function`` 五个键，随后合并调用方 ``kwargs``。
        """
        path = self._params.get_rest_path(request_type)
        extra_data = update_extra_data(
            extra_data,
            **{
                "request_type": request_type,
                "symbol_name": symbol_name,
                "asset_type": self.asset_type,
                "exchange_name": self.exchange_name,
                "normalize_function": normalize_function,
            },
        )
        if kwargs is not None:
            extra_data.update(kwargs)
        return path, params, extra_data

    def _rest(self, name: str, *args: Any, **kwargs: Any) -> Any:
        """同步调用端点 ``self._<name>`` 并发出请求。"""
        path, params, extra_data = getattr(self, f"_{name}")(*args, **kwargs)
        return self.request(path, params=params, extra_data=extra_data)  # type: ignore[attr-defined]

    def _rest_async(self, name: str, *args: Any, **kwargs: Any) -> None:
        """异步提交端点 ``self._<name>`` 的请求。"""
        path, params, extra_data = getattr(self, f"_{name}")(*args, **kwargs)
        self.submit(  # type: ignore[attr-defined]
            self.async_request(path, params=params, extra_data=extra_data),  # type: ignore[attr-defined]
            callback=self.async_callback,  # type: ignore[attr-defined]
        )
