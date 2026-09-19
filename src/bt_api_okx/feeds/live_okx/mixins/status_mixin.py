"""
OKX API - StatusMixin
Auto-generated from request_base.py
"""

from __future__ import annotations

from collections.abc import Callable
from typing import Any

from bt_api_okx.feeds.live_okx.mixins.rest_call_mixin import RestCallMixin


class StatusMixin(RestCallMixin):
    """Mixin providing OKX API methods."""

    _params: Any
    asset_type: str
    exchange_name: str
    request: Callable[..., Any]
    submit: Callable[..., Any]
    async_request: Callable[..., Any]
    async_callback: Callable[..., Any]

    # ==================== Status/Announcement APIs ====================

    def _get_system_status(
        self, state: Any = None, extra_data: Any = None, **kwargs: Any
    ) -> tuple[str, dict[str, Any], dict[str, Any]]:
        """Get system status (maintenance, degraded, etc.)
        Args: state: Status type. "scheduled" for maintenance announcements. Default is empty for current system status.
            extra_data: extra_data, default is None, can be a dict passed by user
            kwargs: pass key-worded, variable-length arguments.
        """
        params: dict[str, Any] = {}
        if state is not None:
            params["state"] = state
        return self._finish(
            "get_system_status",
            params,
            extra_data,
            "SYSTEM",
            StatusMixin._get_system_status_normalize_function,
            kwargs,
        )

    @staticmethod
    def _get_system_status_normalize_function(
        input_data: Any, extra_data: Any
    ) -> tuple[list[Any], bool]:
        """Normalize system status response
        Returns: (status_list, status_bool) where status_list contains system status data
        """
        status = input_data.get("code") == "0"
        if "data" not in input_data or not input_data["data"]:
            return [], status
        return input_data["data"], status

    def get_system_status(
        self, state: Any = None, extra_data: Any = None, **kwargs: Any
    ) -> Any:
        """Get system status
        Args: state: Status type. "scheduled" for maintenance announcements. Default is empty for current system status.
            extra_data: extra_data, default is None, can be a dict passed by user
        """
        return self._rest("get_system_status", state, extra_data, **kwargs)

    def async_get_system_status(
        self, state: Any = None, extra_data: Any = None, **kwargs: Any
    ) -> None:
        """Async get system status
        Args: state: Status type. "scheduled" for maintenance announcements. Default is empty for current system status.
            extra_data: extra_data, default is None, can be a dict passed by user
        """
        return self._rest_async("get_system_status", state, extra_data, **kwargs)

    def _get_announcements(
        self,
        announcement_type: Any = None,
        page: Any = None,
        limit: Any = None,
        extra_data: Any = None,
        **kwargs: Any,
    ) -> tuple[str, dict[str, Any], dict[str, Any]]:
        """Get announcements
        Args: announcement_type: Announcement type. Default is empty for all types.
            page: Page number. Default is 1.
            limit: Number of results per page. Default is 10. Maximum is 100.
            extra_data: extra_data, default is None, can be a dict passed by user
            kwargs: pass key-worded, variable-length arguments.
        """
        params: dict[str, Any] = {}
        if announcement_type is not None:
            params["announcementType"] = announcement_type
        if page is not None:
            params["page"] = str(page)
        if limit is not None:
            params["limit"] = str(limit)
        return self._finish(
            "get_announcements",
            params,
            extra_data,
            "SYSTEM",
            StatusMixin._get_announcements_normalize_function,
            kwargs,
        )

    @staticmethod
    def _get_announcements_normalize_function(
        input_data: Any, extra_data: Any
    ) -> tuple[list[Any], bool]:
        """Normalize announcements response
        Returns: (announcement_list, status_bool) where announcement_list contains announcement data
        """
        status = input_data.get("code") == "0"
        if "data" not in input_data or not input_data["data"]:
            return [], status
        # Return the announcement details directly
        if "details" in input_data["data"][0]:
            return input_data["data"][0]["details"], status
        return input_data["data"], status

    def get_announcements(
        self,
        announcement_type: Any = None,
        page: Any = None,
        limit: Any = None,
        extra_data: Any = None,
        **kwargs: Any,
    ) -> Any:
        """Get announcements
        Args: announcement_type: Announcement type. Default is empty for all types.
            page: Page number. Default is 1.
            limit: Number of results per page. Default is 10. Maximum is 100.
            extra_data: extra_data, default is None, can be a dict passed by user
        """
        return self._rest("get_announcements", announcement_type, page, limit, extra_data, **kwargs)

    def async_get_announcements(
        self,
        announcement_type: Any = None,
        page: Any = None,
        limit: Any = None,
        extra_data: Any = None,
        **kwargs: Any,
    ) -> None:
        """Async get announcements
        Args: announcement_type: Announcement type. Default is empty for all types.
            page: Page number. Default is 1.
            limit: Number of results per page. Default is 10. Maximum is 100.
            extra_data: extra_data, default is None, can be a dict passed by user
        """
        return self._rest_async("get_announcements", announcement_type, page, limit, extra_data, **kwargs)

    def _get_announcement_types(
        self, extra_data: Any = None, **kwargs: Any
    ) -> tuple[str, dict[str, Any], dict[str, Any]]:
        """Get announcement types
        Args: extra_data: extra_data, default is None, can be a dict passed by user
            kwargs: pass key-worded, variable-length arguments.
        """
        params: dict[str, Any] = {}
        return self._finish(
            "get_announcement_types",
            params,
            extra_data,
            "SYSTEM",
            StatusMixin._get_announcement_types_normalize_function,
            kwargs,
        )

    @staticmethod
    def _get_announcement_types_normalize_function(
        input_data: Any, extra_data: Any
    ) -> tuple[Any, bool]:
        """Normalize announcement types response
        Returns: (type_list, status_bool) where type_list contains announcement type data
        """
        status = input_data.get("code") == "0"
        if "data" not in input_data or not input_data["data"]:
            return [], status
        # Return the announcement types directly
        if "announcementType" in input_data["data"][0]:
            return input_data["data"][0]["announcementType"], status
        return input_data["data"], status

    def get_announcement_types(self, extra_data: Any = None, **kwargs: Any) -> Any:
        """Get announcement types
        Args: extra_data: extra_data, default is None, can be a dict passed by user
        """
        return self._rest("get_announcement_types", extra_data, **kwargs)

    def async_get_announcement_types(
        self, extra_data: Any = None, **kwargs: Any
    ) -> None:
        """Async get announcement types
        Args: extra_data: extra_data, default is None, can be a dict passed by user
        """
        return self._rest_async("get_announcement_types", extra_data, **kwargs)
