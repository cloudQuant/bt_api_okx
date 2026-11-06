"""Iteration 62: OKX SWAP ``tickers`` tick channel (fake WSS frames, no network).

The real ``_OwnedOkxMarketWssDataSwap`` is built for the demo route; only its
``start``/``stop`` are replaced by a fake lifecycle, and JSON frames enter
through the real ``on_message`` -> ``message_rsp`` -> ``handle_data`` path.
Evidence level: UNIT/FAKE; the owner test is INTEGRATION_SIM against the
in-process SDK ``ProviderMarketStreamOwner``.
"""

from __future__ import annotations

import json
import threading
import time
from types import SimpleNamespace

import pytest
from bt_api_base.market_protocol import MarketInstrumentKey
from bt_api_base.market_stream_protocol import MarketStreamRequest
from bt_api_base.market_stream_provider_protocol import (
    MarketStreamChannelCapability,
    MarketStreamProviderContractError,
    SelectedMarketStreamRoute,
)
from bt_api_base.market_tick_protocol import (
    MarketClockQuality,
    MarketFreshnessStatus,
    MarketTickEvent,
    MarketTickPayload,
)
from bt_api_okx.feeds.live_okx.swap import OkxRequestDataSwap
from bt_api_okx.market_stream_provider import OkxMarketStreamAdapter
from bt_api_okx.market_tick_stream import (
    OkxTickMarketStreamSession,
    _TickChannel,
    project_okx_quote,
    trade_volume,
)

ROUTE = "OKX___SWAP"
INST = "BTC-USDT-SWAP"
KEY = MarketInstrumentKey("okx", "OKX", "demo", "SWAP", INST, INST)


def _fake_lifecycle(stream, streams):
    def start(connect_timeout=30):
        stream._stop_event = threading.Event()
        stream._connection_generation += 1
        stream._running_flag = True
        stream.data_queue.lifecycle("opened", stream._connection_generation)

    def stop():
        stream._running_flag = False
        stream._stop_event.set()
        stream.ws = None

    stream.start = start
    stream.stop = stop
    streams.append(stream)
    return stream


def _reconnect(stream):
    stream.data_queue.lifecycle("closed", stream._connection_generation)
    stream._connection_generation += 1
    stream.data_queue.lifecycle("opened", stream._connection_generation)


def _frame(stream, inst=INST, **fields):
    row = {
        "instType": "SWAP",
        "instId": inst,
        "last": "60000.5",
        "lastSz": "1",
        "askPx": "60001",
        "askSz": "12",
        "bidPx": "60000",
        "bidSz": "7",
        "vol24h": "123456",
        "ts": "1794020400123",
    }
    row.update(fields)
    stream.on_message(None, json.dumps({"arg": {"channel": "tickers", "instId": inst}, "data": [row]}))


def _trades(stream, *rows):
    data = [
        {"instId": INST, "tradeId": trade_id, "px": px, "sz": sz, "side": "buy",
         "ts": "1794020400500", "count": count}
        for trade_id, px, sz, count in rows
    ]
    stream.on_message(None, json.dumps({"arg": {"channel": "trades", "instId": INST}, "data": data}))


class _Log:
    """Captures the session's warnings (the ``bt_api_base`` logger proxy API)."""

    def __init__(self):
        self.warnings: list = []

    def warning(self, *args, **_kwargs):
        self.warnings.append(args[0] % args[1:] if len(args) > 1 else args[0])


@pytest.fixture
def env():
    feed = OkxRequestDataSwap(None, environment="demo")
    route = SelectedMarketStreamRoute(ROUTE, feed, KEY, "demo")
    wakes: list = []
    streams: list = []
    session = OkxTickMarketStreamSession(route, wake_callback=lambda: wakes.append(1))
    default = session._default_stream
    session._stream_factory = lambda queue, params, info: _fake_lifecycle(
        default(queue, params, info), streams
    )
    log = _Log()
    clock = SimpleNamespace(now=1000.0)
    session._logger = log  # no file logger in tests
    session._log_clock = lambda: clock.now
    yield SimpleNamespace(
        feed=feed, route=route, session=session, streams=streams, wakes=wakes, log=log, clock=clock
    )
    feed._http_client.close()


def _subscribe(env):
    binding = env.session.subscribe(MarketStreamRequest(ROUTE, KEY, "tick"))
    return binding, env.streams[0]


def test_adapter_advertises_tick_only_and_opens_a_tick_session(env):
    adapter = OkxMarketStreamAdapter(env.route)
    assert adapter.capabilities() == (MarketStreamChannelCapability(channel="tick"),)
    session = adapter.open_session(wake_callback=lambda: None)
    assert type(session) is OkxTickMarketStreamSession
    with pytest.raises(MarketStreamProviderContractError):
        env.session.subscribe(MarketStreamRequest(ROUTE, KEY, "orderbook", depth=5))


def test_subscribe_binds_the_demo_tickers_source(env):
    binding, stream = _subscribe(env)
    assert stream.wss_url.startswith("wss://wspap.okx.com")  # demo host
    assert stream.topics == [
        {"topic": "tickers", "symbol": INST},
        {"topic": "trades", "symbol": INST},
    ]
    source = binding.source
    assert source.provider == "okx" and source.source == "okx-public-wss-v5-tickers-trades"
    assert source.connection_generation == 1 and binding.initial_events == ()
    assert binding.key.channel == "tick" and binding.key.instrument == KEY
    assert binding.initial_cursor is None and binding.recovery_required is False


def test_ticks_carry_venue_quotes_times_and_continuity(env):
    binding, stream = _subscribe(env)
    _frame(stream)
    _frame(stream, last="60002", ts="1794020400456")
    first, second = env.session.poll(timeout_ms=0, max_events=10)
    assert all(type(event) is MarketTickEvent for event in (first, second))
    assert first.source == binding.source and [first.cursor.sequence, second.cursor.sequence] == [1, 2]
    tick = first.data
    assert (tick.last_price, tick.bid_price, tick.ask_price) == (60000.5, 60000.0, 60001.0)
    assert (tick.bid_size, tick.ask_size) == (7.0, 12.0)
    assert tick.provider_event_time_utc == "2026-11-07T03:00:00.123000Z"
    assert tick.event_time_provenance == "provider_reported"
    assert tick.received_at_utc is not None and tick.received_monotonic_ns > 0
    assert tick.source_clock_quality is MarketClockQuality.UNKNOWN
    assert tick.receive_clock_quality is MarketClockQuality.UNKNOWN
    assert tick.freshness_status is MarketFreshnessStatus.UNAVAILABLE
    assert tick.execution_eligible is False
    # A quote tick carries no trade; before any trade the volume is a baseline.
    assert (tick.cumulative_volume, tick.delta_volume, tick.volume_complete) == (None, 0.0, False)
    assert tick.volume_quality == "baseline" and tick.turnover is None and tick.quality_flags == ()
    assert tick.continuity_status == "gap" and second.data.continuity_status == "continuous"
    assert tick.provider_connection_generation == 1
    assert second.data.provider_sequence == tick.provider_sequence + 1
    assert MarketTickPayload.from_dict(tick.to_dict()) == tick  # wire-compatible


def test_lost_or_foreign_frames_make_the_next_tick_a_gap(env):
    _binding, stream = _subscribe(env)
    _frame(stream)
    _frame(stream, bidPx="not-a-number")
    _frame(stream, inst="ETH-USDT-SWAP")
    _frame(stream)
    events = env.session.poll(timeout_ms=0, max_events=10)
    assert [event.data.continuity_status for event in events] == ["gap", "gap"]
    assert [event.cursor.sequence for event in events] == [1, 2]
    assert env.session.counters["tick_frame_invalid"] == 2  # malformed + foreign instrument


def test_missing_venue_fields_stay_none_and_missing_ts_is_unavailable(env):
    binding, _stream = _subscribe(env)
    payload = project_okx_quote(
        {"instId": INST, "last": "1", "bidPx": "", "askPx": "", "bidSz": "", "askSz": "", "ts": ""},
        _TickChannel(binding, 1),
        sequence=1,
        received_ns=None,
        received_monotonic_ns=None,
    )
    assert payload.bid_price is None and payload.ask_size is None
    assert payload.provider_event_time_utc is None
    assert payload.event_time_provenance == "unavailable"


def test_reconnect_requires_resync_to_a_new_epoch(env):
    binding, stream = _subscribe(env)
    _frame(stream)
    assert len(env.session.poll(timeout_ms=0, max_events=10)) == 1
    _reconnect(stream)
    _frame(stream)
    with pytest.raises(MarketStreamProviderContractError) as info:
        env.session.poll(timeout_ms=0, max_events=10)
    assert info.value.code == "MARKET_STREAM_PROVIDER_EVENT_INVALID"
    _frame(stream)
    assert env.session.poll(timeout_ms=0, max_events=10) == ()  # recovering: dropped
    with pytest.raises(MarketStreamProviderContractError):
        env.session.resync(binding, acknowledge_data_loss=False)
    renewed = env.session.resync(binding, acknowledge_data_loss=True)
    assert renewed.source.stream_id == binding.source.stream_id
    assert renewed.source.epoch != binding.source.epoch
    assert renewed.source.connection_generation == 2
    _frame(stream)
    (event,) = env.session.poll(timeout_ms=0, max_events=10)
    assert event.source == renewed.source and event.cursor.sequence == 1
    assert event.data.continuity_status == "gap"
    with pytest.raises(MarketStreamProviderContractError):
        env.session.resync(renewed, acknowledge_data_loss=True)  # not recovering


def test_unsubscribe_and_close_stop_the_stream(env):
    binding, stream = _subscribe(env)
    assert env.session.unsubscribe(binding) is True
    assert stream._running_flag is False and stream._stop_event.is_set()
    assert env.session.close() is True


def test_sdk_owner_delivers_ticks_through_the_registered_provider(monkeypatch):
    # Discovers the provider through the installed bt_api.market_stream_providers
    # entry point, as BtApi.market_stream() does.
    owner_module = pytest.importorskip("bt_api_py.service_market_stream_owner")
    feed = OkxRequestDataSwap(None, environment="demo")
    streams: list = []
    original = OkxTickMarketStreamSession._default_stream
    monkeypatch.setattr(
        OkxTickMarketStreamSession,
        "_default_stream",
        lambda self, queue, params, info: _fake_lifecycle(original(self, queue, params, info), streams),
    )
    api = SimpleNamespace(
        exchange_feeds={ROUTE: feed},
        _selected_route_clients={ROUTE: feed},
        _selected_provider_route=lambda name: (feed, "demo"),
    )
    owner = owner_module.ProviderMarketStreamOwner(api)
    try:
        subscription = owner.subscribe(MarketStreamRequest(ROUTE, KEY, "tick"))
        _frame(streams[0])
        _frame(streams[0], last="60003")
        result = owner.poll(subscription, timeout_ms=0, max_events=10)
        assert [event.data.last_price for event in result.events] == [60000.5, 60003.0]
        assert result.state.value == "active"
    finally:
        owner.close()
        feed._http_client.close()


def test_a_disconnect_alone_surfaces_recovery_without_waiting_for_data(env):
    _binding, stream = _subscribe(env)
    _frame(stream)
    env.session.poll(timeout_ms=0, max_events=10)
    stream.data_queue.lifecycle("closed", stream._connection_generation)
    with pytest.raises(MarketStreamProviderContractError):
        env.session.poll(timeout_ms=0, max_events=10)
    assert env.session.counters["recovery:disconnected"] == 1


# ------------------------------------------------------------ traded volume


def _volume(event):
    data = event.data
    return (data.delta_volume, data.volume_complete, data.volume_quality, data.continuity_status)


def test_trades_carry_delta_volume_after_a_baseline(env):
    _binding, stream = _subscribe(env)
    _frame(stream)
    _trades(stream, ("100", "60000.1", "5", "1"))
    _trades(stream, ("101", "60000.2", "3", "1"))
    _trades(stream, ("104", "60000.3", "2", "3"))  # tradeId = last id of 3 aggregated trades
    _frame(stream)
    quote, baseline, first, aggregated, after = env.session.poll(timeout_ms=0, max_events=10)
    assert _volume(quote) == (0.0, False, "baseline", "gap")
    assert _volume(baseline) == (0.0, False, "baseline", "continuous")
    assert baseline.data.last_price == 60000.1 and baseline.data.bid_price == 60000.0
    assert _volume(first) == (3.0, True, "continuous", "continuous")
    assert _volume(aggregated) == (2.0, True, "continuous", "continuous")
    assert aggregated.data.provider_event_time_utc == "2026-11-07T03:00:00.500000Z"
    assert _volume(after) == (0.0, True, "continuous", "continuous")
    assert all(event.data.quality_flags == () for event in (quote, baseline, first, aggregated, after))
    # Contiguous ids are not jumps: nothing counted, nothing logged.
    assert "trade_id_jump" not in env.session.counters and env.log.warnings == []


@pytest.mark.parametrize(
    "jump_id, jump_count, size",
    [
        ("105", "1", 4),  # ids 101..104 never arrived
        ("102", "3", -1),  # a 3-trade aggregate ending at 102 overlaps id 100
    ],
)
def test_a_trade_id_jump_keeps_continuity_and_marks_only_its_row_volume_incomplete(
    env, jump_id, jump_count, size
):
    # User decision 2026-11-06: an uninterrupted connection is continuous; a
    # jump only makes that row's volume accounting incomplete.
    binding, stream = _subscribe(env)
    _frame(stream)
    _trades(stream, ("100", "1", "5", "1"))
    _trades(stream, (jump_id, "1", "4", jump_count))
    _trades(stream, (str(int(jump_id) + 1), "1", "2", "1"))
    _frame(stream)
    _quote, _baseline, jump, resumed, quote = env.session.poll(timeout_ms=0, max_events=10)
    assert _volume(jump) == (4.0, False, "discontinuous", "continuous")
    assert _volume(resumed) == (2.0, True, "continuous", "continuous")
    assert _volume(quote) == (0.0, True, "continuous", "continuous")
    assert all(event.data.quality_flags == () for event in (jump, resumed, quote))
    assert env.session.counters["trade_id_jump"] == 1
    assert "trade_id_gap" not in env.session.counters
    assert env.session.trade_id_jumps(binding) == 1
    (warning,) = env.log.warnings
    assert f"instrument={INST}" in warning and f"jump={size} " in warning
    assert "binding_jumps=1 " in warning and "suppressed=0" in warning


def test_trade_volume_reports_the_signed_jump_size():
    channel = _TickChannel(SimpleNamespace(), 1)
    assert trade_volume(channel, 100, 1, 5.0) == (0.0, False, "baseline", 0)
    assert trade_volume(channel, 101, 1, 3.0) == (3.0, True, "continuous", 0)
    assert trade_volume(channel, 110, 2, 4.0) == (4.0, False, "discontinuous", 7)
    assert trade_volume(channel, 110, 1, 4.0) is None  # repeated id
    assert channel.trade_anchor == 110


def test_trade_id_jump_warnings_are_throttled_per_instrument_but_every_jump_counts(env):
    binding, stream = _subscribe(env)
    _trades(stream, ("100", "1", "5", "1"))
    _trades(stream, ("105", "1", "1", "1"))
    events = list(env.session.poll(timeout_ms=0, max_events=10))  # first jump: logged
    env.clock.now += 59.0
    _trades(stream, ("110", "1", "1", "1"))
    events += env.session.poll(timeout_ms=0, max_events=10)
    assert [event.data.continuity_status for event in events] == ["gap", "continuous", "continuous"]
    assert len(env.log.warnings) == 1  # the second jump is inside the minute
    env.clock.now += 1.0
    _trades(stream, ("120", "1", "1", "1"))
    (event,) = env.session.poll(timeout_ms=0, max_events=10)
    assert _volume(event) == (1.0, False, "discontinuous", "continuous")
    assert len(env.log.warnings) == 2
    assert "jump=9 " in env.log.warnings[1] and "binding_jumps=3 " in env.log.warnings[1]
    assert "suppressed=1" in env.log.warnings[1]
    assert env.session.counters["trade_id_jump"] == 3
    assert env.session.trade_id_jumps(binding) == 3


def test_a_failing_jump_logger_never_stops_the_stream(env):
    binding, stream = _subscribe(env)

    class _Broken:
        def warning(self, *_args, **_kwargs):
            raise RuntimeError("sink down")

    env.session._logger = _Broken()
    _trades(stream, ("100", "1", "5", "1"))
    _trades(stream, ("105", "1", "1", "1"))
    _baseline, jump = env.session.poll(timeout_ms=0, max_events=10)
    assert _volume(jump) == (1.0, False, "discontinuous", "continuous")
    assert env.session.trade_id_jumps(binding) == 1
    assert env.session.counters["trade_id_jump_log_failed"] == 1


def test_repeated_trade_ids_are_not_counted_twice_and_rows_follow_trade_id_order(env):
    _binding, stream = _subscribe(env)
    _frame(stream)
    _trades(stream, ("100", "1", "5", "1"))
    _trades(stream, ("102", "1", "2", "1"), ("101", "1", "1", "1"))  # newest first in one push
    _trades(stream, ("102", "1", "2", "1"))
    events = env.session.poll(timeout_ms=0, max_events=10)
    assert [_volume(e)[:2] for e in events[2:]] == [(1.0, True), (2.0, True)]
    assert len(events) == 4
    assert env.session.counters["trade_repeated_or_out_of_order"] == 1
    # Ignored rows are neither jumps nor continuity defects.
    assert [_volume(e)[3] for e in events[1:]] == ["continuous"] * 3
    assert "trade_id_jump" not in env.session.counters and env.log.warnings == []


def test_the_first_tick_of_a_binding_is_a_gap_even_when_it_is_a_trade(env):
    _binding, stream = _subscribe(env)
    _trades(stream, ("100", "1", "5", "1"))
    _trades(stream, ("101", "1", "3", "1"))
    first, second = env.session.poll(timeout_ms=0, max_events=10)
    assert _volume(first) == (0.0, False, "baseline", "gap")
    assert _volume(second) == (3.0, True, "continuous", "continuous")


def test_a_malformed_trade_row_still_makes_the_next_tick_a_gap(env):
    _binding, stream = _subscribe(env)
    _frame(stream)
    _trades(stream, ("100", "1", "5", "1"))
    _trades(stream, ("101", "not-a-number", "1", "1"))  # a lost push
    _trades(stream, ("102", "1", "2", "1"))
    _trades(stream, ("103", "1", "1", "1"))
    _quote, _baseline, after_loss, resumed = env.session.poll(timeout_ms=0, max_events=10)
    assert _volume(after_loss) == (2.0, False, "discontinuous", "gap")
    assert _volume(resumed) == (1.0, True, "continuous", "continuous")
    assert env.session.counters["tick_frame_invalid"] == 1


def test_an_ingress_overflow_still_requires_recovery_and_a_gap_after_resync(env):
    binding = env.session.subscribe(MarketStreamRequest(ROUTE, KEY, "tick", queue_capacity=2))
    stream = env.streams[0]  # its "opened" record already holds one slot
    _trades(stream, ("100", "1", "5", "1"))
    _trades(stream, ("101", "1", "5", "1"))  # does not fit: overflow
    with pytest.raises(MarketStreamProviderContractError):
        env.session.poll(timeout_ms=0, max_events=10)
    assert env.session.counters["recovery:queue_overflow"] == 1
    renewed = env.session.resync(binding, acknowledge_data_loss=True)
    _trades(stream, ("150", "1", "2", "1"))
    (event,) = env.session.poll(timeout_ms=0, max_events=10)
    assert event.source == renewed.source
    assert _volume(event) == (0.0, False, "baseline", "gap")
    assert "trade_id_jump" not in env.session.counters  # a new epoch re-anchors: not a jump


def test_resync_starts_a_new_volume_baseline(env):
    binding, stream = _subscribe(env)
    _trades(stream, ("100", "1", "5", "1"))
    _trades(stream, ("101", "1", "5", "1"))
    env.session.poll(timeout_ms=0, max_events=10)
    _reconnect(stream)
    with pytest.raises(MarketStreamProviderContractError):
        env.session.poll(timeout_ms=0, max_events=10)
    env.session.resync(binding, acknowledge_data_loss=True)
    _trades(stream, ("102", "1", "5", "1"))
    (event,) = env.session.poll(timeout_ms=0, max_events=10)
    assert _volume(event) == (0.0, False, "baseline", "gap")
    assert event.data.bid_price is None  # the quote does not cross epochs


def test_sdk_normalizer_sees_known_delta_volume_semantics(env):
    contracts = pytest.importorskip("bt_api_py.market_tick_contracts")
    _binding, stream = _subscribe(env)
    _frame(stream)
    _trades(stream, ("100", "60000.1", "5", "1"))
    _trades(stream, ("101", "60000.2", "3", "1"))
    for event in env.session.poll(timeout_ms=0, max_events=10):
        data = event.data
        # The fields Backtrader's market_tick_adapter hands to the SDK normalizer.
        tick = SimpleNamespace(
            schema_version="sdk.market.tick.v2",
            volume_semantics="delta" if data.delta_volume is not None else "unknown",
            delta_volume=data.delta_volume,
            volume=data.delta_volume,
            price=data.last_price,
            bid_price=data.bid_price,
            ask_price=data.ask_price,
            bid_volume=data.bid_size,
            ask_volume=data.ask_size,
            quality_flags=list(data.quality_flags),
        )
        prepared = contracts.prepare_market_tick_fields(
            tick, replay_adapter_available=False, legacy_schema="legacy"
        )
        flags = prepared[3]
        assert "VOLUME_SEMANTICS_UNKNOWN" not in flags and "DELTA_VOLUME_INVALID" not in flags
        assert flags == set()


def test_the_jump_count_is_per_binding_and_a_resync_binding_starts_at_zero(env):
    binding, stream = _subscribe(env)
    _trades(stream, ("100", "1", "5", "1"))
    _trades(stream, ("105", "1", "1", "1"))
    env.session.poll(timeout_ms=0, max_events=10)
    assert env.session.trade_id_jumps(binding) == 1
    _reconnect(stream)
    with pytest.raises(MarketStreamProviderContractError):
        env.session.poll(timeout_ms=0, max_events=10)
    renewed = env.session.resync(binding, acknowledge_data_loss=True)
    assert env.session.trade_id_jumps(renewed) == 0
    with pytest.raises(MarketStreamProviderContractError):
        env.session.trade_id_jumps(binding)  # the lost epoch's binding is gone
    assert env.session.counters["trade_id_jump"] == 1  # the session total is kept


def test_sdk_clock_qualification_keeps_a_fresh_trade_id_jump_row_execution_eligible(env):
    """Point 1 of the 2026-11-06 decision: incomplete volume alone is not a trade veto.

    ``bt_api_py.clock_verification`` decides execution eligibility from
    freshness and ``continuity_status`` only; this pins that a fresh jump row
    qualifies while the binding's first (gap) tick still does not.
    """
    clock = pytest.importorskip("bt_api_py.clock_verification")
    _binding, stream = _subscribe(env)
    now_ms = str(time.time_ns() // 1_000_000)
    for trade_id in ("100", "105"):
        stream.on_message(None, json.dumps({
            "arg": {"channel": "trades", "instId": INST},
            "data": [{"instId": INST, "tradeId": trade_id, "px": "1", "sz": "2", "side": "buy",
                      "ts": now_ms, "count": "1"}],
        }))
    first, jump = env.session.poll(timeout_ms=0, max_events=10)
    evidence = clock.ClockEvidence(
        offset_ns=0, error_bound_ns=1_000_000, server="fake-sntp", method="fake",
        measured_monotonic_ns=0, valid_until_monotonic_ns=2**62,
    )
    check = clock.VenueClockCheck(
        consistent=True, difference_ms=0.0, tolerance_ms=50.0, source="fake"
    )
    qualified_first, qualified_jump = (
        clock.qualify_market_tick_event(event, evidence, check, max_latency_seconds=60.0)
        for event in (first, jump)
    )
    assert qualified_jump.data.freshness_status is MarketFreshnessStatus.FRESH
    assert qualified_jump.data.volume_complete is False
    assert qualified_jump.data.volume_quality == "discontinuous"
    assert qualified_jump.data.execution_eligible is True
    assert qualified_first.data.continuity_status == "gap"
    assert qualified_first.data.execution_eligible is False
