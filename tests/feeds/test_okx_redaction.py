"""OKX async and WebSocket diagnostics redact configured credentials."""

import json
import logging
from concurrent.futures import Future

from bt_api_okx.feeds.live_okx.market_wss_base import OkxWssData
from bt_api_okx.feeds.live_okx.request_base import OkxRequestData

API_KEY = "okx-key-that-must-not-leak"
SECRET = "okx-secret-that-must-not-leak"
PASSPHRASE = "okx-passphrase-that-must-not-leak"


def _assert_redacted(value):
    rendered = str(value)
    for secret in (API_KEY, SECRET, PASSPHRASE):
        assert secret not in rendered


def test_async_callback_redacts_literal_credentials(caplog):
    feed = object.__new__(OkxRequestData)
    feed.public_key = API_KEY
    feed.private_key = SECRET
    feed.passphrase = PASSPHRASE
    feed.async_logger = logging.getLogger("test.okx.async.redaction")
    future = Future()
    future.set_exception(RuntimeError(f"opaque {API_KEY} {SECRET} {PASSPHRASE}"))

    with caplog.at_level(logging.WARNING, logger=feed.async_logger.name):
        feed.async_callback(future)

    _assert_redacted(caplog.text)


def test_unknown_websocket_message_redacts_literal_credentials(caplog):
    feed = object.__new__(OkxWssData)
    feed.public_key = API_KEY
    feed.private_key = SECRET
    feed.passphrase = PASSPHRASE
    feed._params = None
    feed.wss_logger = logging.getLogger("test.okx.wss.redaction")
    message = json.dumps({"opaque": f"{API_KEY} {SECRET} {PASSPHRASE}"})

    with caplog.at_level(logging.INFO, logger=feed.wss_logger.name):
        feed.message_rsp(message)

    _assert_redacted(caplog.text)
