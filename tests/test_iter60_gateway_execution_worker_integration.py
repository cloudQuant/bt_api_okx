"""Iteration 60: the real Gateway worker publishes OKX SWAP execution observations.

``GatewayAccountSessionWorker`` + ``GatewayExecutionEventPublisher`` + a
temporary ``GatewayEventJournal`` drive ``OkxSwapDemoAccountSessionProvider``
over a fake transport. NOTE: real OKX ``clOrdId`` allows only alphanumerics, so
the Base strategy prefix (which contains ``-``) cannot be sent to the venue;
this test proves only the Gateway plumbing for such an id.
Evidence: INTEGRATION_SIM (local SQLite, fake venue); no network or account.
"""

from __future__ import annotations

import pytest

pytest.importorskip("bt_api_gateway")

from bt_api_base.execution_row_observation_protocol import (  # noqa: E402
    execution_observation_from_event,
    strategy_client_order_prefix,
)
from test_iter60_gateway_execution_observations import (  # noqa: E402
    Clock,
    FakeIssuer,
    FakeOkxVenue,
    account_key,
    credentials,
    fill_row,
    order_row,
    scope,
)

from bt_api_gateway import GatewayCommandKind, GatewayEventJournal, GatewayPrincipal  # noqa: E402
from bt_api_gateway.account_session_worker import (  # noqa: E402
    GatewayAccountSessionWorker,
    GatewayAccountSessionWorkerError,
)
from bt_api_gateway.execution_event_publisher import (  # noqa: E402
    GatewayExecutionEventPublisher,
    GatewayExecutionScopePolicy,
)
from bt_api_gateway.session_guard import LocalAccountSessionGuard  # noqa: E402
from bt_api_okx.gateway_account_provider import (  # noqa: E402
    ACCOUNT_RESOURCE,
    SWAP_CROSS_RESOURCE,
    OkxSwapDemoAccountSessionProvider,
)

ACCOUNT_SCOPE = "account:okx-demo"
STATE_SCOPE = "strategy:account-facts"
EXEC_A = "exec:strategy-a"
UNATTRIBUTED = "exec:unattributed"


class Deployment:
    def __init__(self, tmp_path, venue, clock, issuer):
        self.tmp_path, self.venue, self.clock, self.issuer = tmp_path, venue, clock, issuer
        (tmp_path / "guards").mkdir(exist_ok=True)
        self.worker = self.provider = self.journal = None

    def start(self):
        """A fresh Gateway process: new provider, worker, generation; same files."""

        if self.worker is not None:
            self.worker.close()
        self.clock.advance(2.0)
        self.journal = GatewayEventJournal(self.tmp_path / "gateway.db", clock=lambda: self.clock.wall)
        key = account_key()
        self.provider = OkxSwapDemoAccountSessionProvider(
            credentials(),
            transport=self.venue,
            wall_clock=lambda: self.clock.wall,
            monotonic_clock=lambda: self.clock.mono,
            execution=scope(self.issuer),
        )
        self.worker = GatewayAccountSessionWorker(
            self.provider,
            self.journal,
            account_key=key,
            journal_account_scope=ACCOUNT_SCOPE,
            state_scope=STATE_SCOPE,
            guard=LocalAccountSessionGuard(self.tmp_path / "guards", key.account_key_id, "owner"),
            required_coverage=(ACCOUNT_RESOURCE, SWAP_CROSS_RESOURCE),
            clock=lambda: self.clock.wall,
            monotonic_clock=lambda: self.clock.mono,
            execution_publisher=GatewayExecutionEventPublisher(
                self.journal,
                account_key=key,
                journal_account_scope=ACCOUNT_SCOPE,
                policy=GatewayExecutionScopePolicy.for_strategies(
                    {"strategy-a": EXEC_A}, unattributed_scope=UNATTRIBUTED
                ),
            ),
        )
        self.worker.start()
        return self.worker

    def events(self, scope_name):
        principal = GatewayPrincipal(
            principal_id="reader",
            account_scopes=frozenset({ACCOUNT_SCOPE}),
            strategy_scopes=frozenset({scope_name}),
            allowed_kinds=frozenset({GatewayCommandKind.READ}),
        )
        batch = self.journal.read_after(principal, ACCOUNT_SCOPE, scope_name, cursor=None, limit=100)
        return [
            execution_observation_from_event(event.kind, event.event_id, event.payload)
            for event in batch.events
        ]


def test_okx_fills_route_by_strategy_prefix_with_fee_corrections_and_restarts(tmp_path):
    clock = Clock()
    venue = FakeOkxVenue(clock=clock)
    prefix = strategy_client_order_prefix("strategy-a")
    venue.add_order(order_row(1001, sz="1", client=prefix + "0001"))
    venue.fills.append(fill_row(9001, 1001, fee="-0.02"))
    venue.add_order(order_row(1002, sz="1", client="manual1"))
    venue.fills.append(fill_row(9002, 1002, fee="-0.01"))
    gateway = Deployment(tmp_path, venue, clock, FakeIssuer())

    worker = gateway.start()
    result = worker.publish_execution_events()
    assert (result.appended, result.duplicates, result.unattributed_dropped) == (4, 0, 0)
    order_a, fill_a = gateway.events(EXEC_A)
    assert order_a.order.client_order_id == prefix + "0001"
    assert fill_a.trade.order_id == order_a.order.order_id and fill_a.fee == "0.02"
    assert len(gateway.events(UNATTRIBUTED)) == 2
    assert worker.publish_execution_events().appended == 0

    venue.fills[0]["fee"] = "-0.03"  # restart; the venue now reports a higher fee
    worker = gateway.start()
    result = worker.publish_execution_events()
    assert (result.appended, result.duplicates) == (1, 3)
    stream_a = gateway.events(EXEC_A)
    assert len(stream_a) == 3
    assert stream_a[2].trade.trade_id == fill_a.trade.trade_id and stream_a[2].fee == "0.03"

    venue.fills[0]["fee"] = "-0.025"  # restart; a lower fee is refused, not confirmed
    worker = gateway.start()
    with pytest.raises(GatewayAccountSessionWorkerError) as refused:
        worker.publish_execution_events()
    assert refused.value.code == "EXECUTION_FEE_REGRESSED"
    redelivered = gateway.provider.read_execution_observations(
        generation=worker.session_generation, timeout=2.0, limit=1000
    )
    assert any(getattr(item, "fee", None) == "0.025" for item in redelivered)
    worker.maintain()
    assert worker.execution_status == "failed:EXECUTION_FEE_REGRESSED"
    assert len(gateway.events(EXEC_A)) == 3

    venue.fills[0]["fee"] = "-0.03"  # consistent again: nothing new after a restart
    worker = gateway.start()
    result = worker.publish_execution_events()
    assert (result.appended, result.duplicates) == (0, 4)
    assert len(gateway.events(EXEC_A)) == 3 and len(gateway.events(UNATTRIBUTED)) == 2
    worker.close()
