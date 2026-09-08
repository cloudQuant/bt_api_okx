"""OKX stateful L2 reconstruction, CRC32 and gap-latch contracts."""

import threading
import zlib
from decimal import Decimal
from queue import Empty, Queue

import pytest
from bt_api_okx.feeds.live_okx.market_wss_base import OkxWssData


def _feed():
    feed = object.__new__(OkxWssData)
    feed.asset_type = "SWAP"
    feed.data_queue = Queue()
    feed._depth_sequences = {}
    feed._depth_gaps = set()
    feed._depth_books = {}
    feed._depth_stale_emitted = set()
    feed._depth_reseed_requested = set()
    feed._depth_lock = threading.RLock()
    feed.reseeded = []
    feed.reseed_event = threading.Event()

    def reseed(key):
        feed.reseeded.append(key)
        feed.reseed_event.set()

    feed._depth_reseed_callback = reseed
    return feed


def _checksum(bids, asks):
    bids = sorted(bids, key=lambda row: Decimal(row[0]), reverse=True)[:25]
    asks = sorted(asks, key=lambda row: Decimal(row[0]))[:25]
    values = []
    for index in range(max(len(bids), len(asks))):
        if index < len(bids):
            values.extend(bids[index][:2])
        if index < len(asks):
            values.extend(asks[index][:2])
    value = zlib.crc32(":".join(values).encode())
    return value - 2**32 if value >= 2**31 else value


def _event(action, sequence, previous, bids, asks, *, checksum=None):
    return {
        "arg": {"channel": "books-l2-tbt", "instId": "BTC-USDT-SWAP"},
        "action": action,
        "data": [
            {
                "ts": "1700000000000",
                "seqId": sequence,
                "prevSeqId": previous,
                "checksum": _checksum(bids, asks) if checksum is None else checksum,
                "bids": bids,
                "asks": asks,
            }
        ],
    }


def _next(feed):
    return feed.data_queue.get_nowait().init_data().get_all_data()


def test_snapshot_large_sequence_jump_and_zero_delete_publish_full_book():
    feed = _feed()
    bids = [["60000", "1", "1", "0"], ["59999", "2", "1", "0"]]
    asks = [["60001", "1", "1", "0"]]
    feed.push_l2_order_book(_event("snapshot", 100, -1, bids, asks))
    snapshot = _next(feed)
    assert snapshot["snapshot_or_delta"] == "snapshot"
    assert snapshot["continuity_status"] == "snapshot"
    assert snapshot["received_monotonic_ns"] > 0 and snapshot["clock_domain_id"]

    # seqId may jump; prevSeqId is the authoritative link.
    final_bids = [["60002", "3", "2", "0"], ["59999", "2", "1", "0"]]
    final_asks = []
    update = _event(
        "update",
        10_001,
        100,
        [["60000", "0", "0", "0"], ["60002", "3", "2", "0"]],
        [["60001", "0", "0", "0"]],
        checksum=_checksum(final_bids, final_asks),
    )
    feed.push_l2_order_book(update)
    rebuilt = _next(feed)
    assert rebuilt["previous_sequence"] == 100
    assert rebuilt["sequence_id"] == 10_001
    assert rebuilt["continuity_status"] == "continuous"
    assert rebuilt["bid_price_list"] == [60002.0, 59999.0]
    assert rebuilt["ask_price_list"] == []


def test_sequence_or_checksum_failure_latches_until_new_valid_snapshot():
    feed = _feed()
    bids = [["60000", "1", "1", "0"]]
    asks = [["60001", "1", "1", "0"]]
    feed.push_l2_order_book(_event("snapshot", 100, -1, bids, asks))
    _next(feed)

    feed.push_l2_order_book(_event("update", 200, 199, bids, asks))
    stale = feed.data_queue.get_nowait()
    assert stale["stale"] is True and stale["stale_reason"] == "sequence_gap"
    assert feed.reseed_event.wait(1)
    feed.push_l2_order_book(_event("update", 201, 200, bids, asks))
    with pytest.raises(Empty):
        feed.data_queue.get_nowait()

    feed.push_l2_order_book(_event("snapshot", 300, -1, bids, asks, checksum=123))
    with pytest.raises(Empty):
        feed.data_queue.get_nowait()

    feed.push_l2_order_book(_event("snapshot", 400, -1, bids, asks))
    recovered = _next(feed)
    assert recovered["continuity_status"] == "snapshot"
    assert not recovered["stale"]
    assert len(feed.reseeded) == 1


def test_l2_special_channel_has_exactly_one_dispatch_path():
    feed = _feed()
    routed = []
    feed.push_l2_order_book = lambda content: routed.append(("l2", content))
    feed.push_order_book = lambda content: routed.append(("regular", content))
    content = _event("snapshot", 1, -1, [], [])
    content["arg"]["channel"] = "books50-l2-tbt"

    feed.handle_data(content)

    assert [name for name, _content in routed] == ["l2"]


def test_nonbook_special_channel_does_not_hit_generic_substring_route():
    feed = _feed()
    routed = []
    feed.push_ticker = lambda content: routed.append(("generic", content))
    feed._push_block_tickers = lambda content: routed.append(("block", content))
    feed.handle_data({"arg": {"channel": "block-tickers"}, "data": [{}]})
    assert [name for name, _content in routed] == ["block"]


def test_sequence_above_float_precision_is_preserved_exactly():
    feed = _feed()
    sequence = 2**53 + 101
    bids = [["60000", "1", "1", "0"]]
    asks = [["60001", "1", "1", "0"]]
    feed.push_l2_order_book(_event("snapshot", sequence, -1, bids, asks))
    assert _next(feed)["sequence_id"] == sequence
