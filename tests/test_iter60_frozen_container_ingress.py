"""Iteration 60: OKX market ingress accepts published (frozen) containers.

``freeze()`` moves a container to a read-only subclass of its class and turns
nested dicts/lists into read-only views, so ``type(x) is OkxL2OrderBookData``
and ``isinstance(row, dict)`` no longer hold for a published book. The
ingress checks use Base ``container_class`` (still exact: a hand-made
subclass is refused) and read the row as a ``Mapping`` with tuple levels.
"""

from __future__ import annotations

from bt_api_base.containers.auto_init_mixin import container_class
from bt_api_okx.containers.orderbooks.okx_l2_orderbook import OkxL2OrderBookData
from bt_api_okx.market_stream_provider import _project_book_state


def _book(cls=OkxL2OrderBookData):
    row = {
        "action": "snapshot",
        "native_action": "snapshot",
        "seqId": 10,
        "prevSeqId": -1,
        "continuity_status": "snapshot",
        "bids": [["100.0", "1.0", "0", "1"], ["99.5", "2.0", "0", "1"]],
        "asks": [["100.5", "3.0", "0", "1"], ["101.0", "4.0", "0", "1"]],
        "ts": "1770000000123",
    }
    book = cls(row, symbol_name="BTC-USDT-SWAP", asset_type="SWAP", has_been_json_encoded=True)
    book.init_data()
    return book


def test_frozen_book_keeps_its_exact_class():
    book = _book().freeze()
    assert type(book) is not OkxL2OrderBookData  # the read-only variant
    assert container_class(book) is OkxL2OrderBookData


def test_hand_made_subclass_is_not_the_exact_class():
    class _Forged(OkxL2OrderBookData):
        pass

    assert container_class(_book(_Forged)) is _Forged


def test_frozen_book_projects_exactly_like_the_unfrozen_one():
    live = _project_book_state(_book(), 1)
    frozen = _book().freeze()
    assert type(frozen.order_book_data) is not dict  # read-only view after freeze
    published = _project_book_state(frozen, 1)
    assert published.bids == live.bids and published.asks == live.asks
    assert (published.provider_sequence, published.snapshot_or_delta) == (10, "snapshot")
    assert published.provider_event_time_utc == live.provider_event_time_utc
