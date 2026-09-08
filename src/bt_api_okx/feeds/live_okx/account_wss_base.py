"""
OKX Account WebSocket base class.
Handles private account channels (orders, account, positions, balance_and_position).
"""

from __future__ import annotations

import math
import threading
import time
from typing import Any

from bt_api_okx.feeds.live_okx.market_wss_base import OkxWssData
from bt_api_okx.feeds.live_okx.request_base import strict_credential_alias


class OkxAccountWssData(OkxWssData):
    """Class OkxAccountWssData"""

    def __init__(self, data_queue: Any, **kwargs: Any) -> None:
        """__init__ method"""
        key = strict_credential_alias(kwargs, ("public_key", "api_key"))
        secret = strict_credential_alias(kwargs, ("private_key", "secret_key", "api_secret"))
        passphrase = strict_credential_alias(kwargs, ("passphrase",))
        if not key or not secret or not passphrase:
            raise ValueError("OKX private websocket requires API key, secret and passphrase")
        requested_url = kwargs.pop("wss_url", None)
        configured_url = kwargs.get("account_wss_url")
        if requested_url is not None:
            if configured_url is not None and configured_url != requested_url:
                raise ValueError("Conflicting private websocket URLs")
            kwargs["account_wss_url"] = requested_url
        super().__init__(data_queue, **kwargs)
        self._stream_role = "account"
        self.wss_url = self._params.account_wss_url
        raw_ping_interval = kwargs.get("okx_application_ping_interval", 20.0)
        raw_pong_timeout = kwargs.get("okx_application_pong_timeout", 5.0)
        if isinstance(raw_ping_interval, bool) or isinstance(raw_pong_timeout, bool):
            raise ValueError("OKX application heartbeat intervals must be finite positive numbers")
        self.okx_application_ping_interval = float(raw_ping_interval)
        self.okx_application_pong_timeout = float(raw_pong_timeout)
        if (
            not math.isfinite(self.okx_application_ping_interval)
            or not math.isfinite(self.okx_application_pong_timeout)
            or self.okx_application_ping_interval <= 0
            or self.okx_application_pong_timeout <= 0
            or self.okx_application_ping_interval + self.okx_application_pong_timeout >= 30
        ):
            raise ValueError(
                "OKX application heartbeat must use finite positive intervals totaling under 30s"
            )
        self._okx_heartbeat_lock = threading.Lock()
        self._okx_heartbeat_process: threading.Thread | None = None
        self._okx_ping_sent_at: float | None = None
        self._okx_ping_generation = 0
        self._okx_ping_ws = None

    def start(self, connect_timeout=30):
        """Start the stream and its OKX text ping/pong heartbeat."""
        super().start(connect_timeout=connect_timeout)
        worker = self._okx_heartbeat_process
        if worker is None or not worker.is_alive():
            self._okx_heartbeat_process = threading.Thread(
                target=self._okx_application_heartbeat,
                daemon=True,
            )
            self._okx_heartbeat_process.start()

    def stop(self):
        """Stop the stream and join its application heartbeat worker."""
        failure = None
        try:
            super().stop()
        except Exception as error:
            failure = error
        worker = self._okx_heartbeat_process
        current = threading.current_thread()
        if worker is not None and worker is not current and worker.is_alive():
            worker.join(timeout=self._shutdown_timeout)
            if worker.is_alive():
                cleanup_error = RuntimeError(
                    "OKX application heartbeat worker did not stop within shutdown_timeout"
                )
                if failure is not None:
                    raise cleanup_error from failure
                raise cleanup_error
        if failure is not None:
            raise failure

    @staticmethod
    def _is_application_pong(message: Any) -> bool:
        return message == "pong" or message == b"pong"

    def on_message(self, _ws, message):
        """Consume OKX text pong without passing it to the JSON decoder."""
        if self._is_application_pong(message):
            self._last_message_at = time.monotonic()
            with self._okx_heartbeat_lock:
                if (
                    self._okx_ping_ws is _ws
                    and self._okx_ping_generation == self._connection_generation
                ):
                    self._okx_ping_sent_at = None
                    self._okx_ping_ws = None
            return
        super().on_message(_ws, message)

    def _clear_application_ping(self, expected_ws, generation) -> None:
        with self._okx_heartbeat_lock:
            if self._okx_ping_ws is expected_ws and self._okx_ping_generation == generation:
                self._okx_ping_sent_at = None
                self._okx_ping_ws = None

    def _close_application_heartbeat_generation(
        self, expected_ws, generation, event_type, **payload
    ) -> None:
        if self.ws is not expected_ws or self._connection_generation != generation:
            self._clear_application_ping(expected_ws, generation)
            return
        self._clear_application_ping(expected_ws, generation)
        self._running_flag = False
        self._emit_event(event_type, heartbeat_generation=generation, **payload)
        try:
            expected_ws.close()
        except Exception as error:
            self._log_callback_failure(error)

    def _okx_application_heartbeat(self) -> None:
        """Send OKX text ping after application silence and require its pong."""
        stop_event = self._stop_event
        check_interval = min(
            0.5,
            max(
                0.01,
                min(
                    self.okx_application_ping_interval,
                    self.okx_application_pong_timeout,
                )
                / 4.0,
            ),
        )
        while not stop_event.wait(check_interval):
            now = time.monotonic()
            with self._okx_heartbeat_lock:
                pending_at = self._okx_ping_sent_at
                pending_ws = self._okx_ping_ws
                pending_generation = self._okx_ping_generation
            if pending_at is not None and pending_ws is not None:
                if self.ws is not pending_ws or self._connection_generation != pending_generation:
                    self._clear_application_ping(pending_ws, pending_generation)
                    continue
                if now - pending_at >= self.okx_application_pong_timeout:
                    self._close_application_heartbeat_generation(
                        pending_ws,
                        pending_generation,
                        "ws.application_pong_timeout",
                        timeout_seconds=self.okx_application_pong_timeout,
                    )
                continue
            last_message_at = self._last_message_at
            expected_ws = self.ws
            generation = self._connection_generation
            if (
                not self._running_flag
                or last_message_at is None
                or expected_ws is None
                or now - last_message_at < self.okx_application_ping_interval
            ):
                continue
            with self._okx_heartbeat_lock:
                if self._okx_ping_sent_at is not None:
                    continue
                self._okx_ping_sent_at = now
                self._okx_ping_generation = generation
                self._okx_ping_ws = expected_ws
            if self.ws is not expected_ws or self._connection_generation != generation:
                self._clear_application_ping(expected_ws, generation)
                continue
            try:
                expected_ws.send("ping")
            except Exception as error:
                self._close_application_heartbeat_generation(
                    expected_ws,
                    generation,
                    "ws.application_ping_error",
                    error=self._safe_failure(error),
                )


class OkxMarketWssData(OkxWssData):
    """Class OkxMarketWssData"""

    def __init__(self, data_queue: Any, **kwargs: Any) -> None:
        """__init__ method"""
        super().__init__(data_queue, **kwargs)
        self.wss_url = kwargs.get("wss_url", self._params.wss_url)


class OkxKlineWssData(OkxWssData):
    """Class OkxKlineWssData"""

    def __init__(self, data_queue: Any, **kwargs: Any) -> None:
        """__init__ method"""
        requested_url = kwargs.pop("wss_url", None)
        configured_url = kwargs.get("kline_wss_url")
        if requested_url is not None:
            if configured_url is not None and configured_url != requested_url:
                raise ValueError("Conflicting business websocket URLs")
            kwargs["kline_wss_url"] = requested_url
        super().__init__(data_queue, **kwargs)
        self.wss_url = self._params.kline_wss_url
