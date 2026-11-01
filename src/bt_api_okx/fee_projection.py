"""OKX fee scope and native commission/rebate projection.

Neutral constructors and value readers are supplied by the SDK caller.
"""
from decimal import Decimal
from types import SimpleNamespace

_OKX_SPOT_FEE_TYPES = frozenset({"SPOT", "MARGIN"})
_OKX_DERIVATIVE_FEE_TYPES = frozenset({"SWAP", "FUTURES", "OPTION"})


def create_fee_projection(dependencies):
    rows = dependencies["rows"]
    pick = dependencies["pick"]
    decimal_number = dependencies["decimal_number"]
    _unavailable_fee_schedule = dependencies["unavailable_fee_schedule"]
    _freshness = dependencies["freshness"]
    FeeSchedule = dependencies["fee_schedule_type"]
    NormalizedApiError = dependencies["normalized_error"]
    CapabilityNotSupportedError = dependencies["unsupported_error"]

    def _okx_fee_asset_type(value):
        asset_type = str(value or "").strip().upper()
        return "FUTURES" if asset_type == "FUTURE" else asset_type

    def _okx_fee_instrument_id(symbol, asset_type):
        inst_id = str(symbol or "").strip().replace("/", "-").upper()
        if asset_type == "SWAP" and inst_id and (not inst_id.endswith("-SWAP")):
            inst_id += "-SWAP"
        return inst_id

    def _compact_instrument_id(value):
        return "".join((character for character in str(value or "").upper() if character.isalnum()))

    def okx_fee_scope(result, exchange_name, symbol):
        """Resolve the exact OKX fee-query identity from public instrument metadata."""
        if str(exchange_name).partition("___")[0].upper() != "OKX":
            raise CapabilityNotSupportedError(
                "get_fee_schedule", detail="OKX fee scope requested for another venue"
            )
        asset_type = _okx_fee_asset_type(str(exchange_name).partition("___")[2])
        if asset_type not in _OKX_SPOT_FEE_TYPES | _OKX_DERIVATIVE_FEE_TYPES:
            raise NormalizedApiError("get_fee_schedule", "unsupported_fee_instrument_type")
        expected_inst_id = _okx_fee_instrument_id(symbol, asset_type)
        expected_compact = _compact_instrument_id(expected_inst_id)
        source = rows(result, "get_fee_instrument_metadata", exchange_name=exchange_name)
        matches = []
        for row in source:
            row_inst_id = str(pick(row, "instId", "symbol", "symbol_name", default="")).strip()
            row_asset_type = _okx_fee_asset_type(
                pick(row, "instType", "asset_type", default=asset_type)
            )
            if (
                row_asset_type == asset_type
                and _compact_instrument_id(row_inst_id) == expected_compact
            ):
                matches.append((row, row_inst_id))
        if not matches:
            raise NormalizedApiError("get_fee_schedule", "fee_instrument_metadata_not_found")
        if len(matches) != 1:
            raise NormalizedApiError("get_fee_schedule", "fee_instrument_metadata_ambiguous")
        row, inst_id = matches[0]
        group_id_value = pick(row, "groupId", "group_id")
        group_id = str(group_id_value).strip() if group_id_value not in (None, "") else None
        scope = {
            "asset_type": asset_type,
            "inst_id": inst_id,
            "inst_family": None,
            "group_id": group_id,
            "currency": pick(row, "settleCcy", "quoteCcy", "fee_currency"),
        }
        if asset_type in _OKX_DERIVATIVE_FEE_TYPES:
            inst_family = str(pick(row, "instFamily", "underlying_symbol_name", default="")).strip()
            if not inst_family:
                raise NormalizedApiError("get_fee_schedule", "fee_inst_family_missing")
            scope["inst_family"] = inst_family
        return scope

    def _okx_legacy_fee_fields(symbol, asset_type):
        upper_symbol = str(symbol or "").upper()
        if "USDC" in upper_symbol:
            return (("makerUSDC", "maker"), ("takerUSDC", "taker"))
        if asset_type in _OKX_DERIVATIVE_FEE_TYPES and "USDT" in upper_symbol:
            return (("makerU", "maker"), ("takerU", "taker"))
        return (("maker",), ("taker",))

    def _okx_cost_and_rebate(value):
        native_rate = decimal_number(value)
        if native_rate is None:
            return (None, None)
        if native_rate < 0:
            return (-native_rate, Decimal("0"))
        if native_rate > 0:
            return (Decimal("0"), native_rate)
        return (Decimal("0"), Decimal("0"))

    def fee_schedule(
        result, exchange_name, symbol, account_id, *, expected_group_id=None, metadata_currency=None
    ):
        source = rows(result, "get_fee_schedule", exchange_name=exchange_name)
        venue = exchange_name.partition("___")[0].upper()
        asset_type = _okx_fee_asset_type(exchange_name.partition("___")[2])
        typed_rows = [
            row
            for row in source
            if _okx_fee_asset_type(pick(row, "instType", default=asset_type)) == asset_type
        ]
        if not typed_rows:
            return _unavailable_fee_schedule(
                exchange_name, symbol, account_id, {}, "fee_asset_type_missing"
            )
        if len(typed_rows) != 1:
            return _unavailable_fee_schedule(
                exchange_name, symbol, account_id, {}, "fee_asset_type_ambiguous"
            )
        row = typed_rows[0]
        selected_group_id = None
        native_maker = None
        native_taker = None
        if row.get("feeGroup") not in (None, []):
            fee_groups = row["feeGroup"]
            if not isinstance(fee_groups, list) or not all(
                (isinstance(group, dict) for group in fee_groups)
            ):
                return _unavailable_fee_schedule(
                    exchange_name, symbol, account_id, row, "fee_group_payload_invalid"
                )
            if expected_group_id not in (None, ""):
                group_matches = [
                    group
                    for group in fee_groups
                    if str(group.get("groupId", "")).strip() == str(expected_group_id).strip()
                ]
            else:
                group_matches = fee_groups
            if not group_matches:
                return _unavailable_fee_schedule(
                    exchange_name, symbol, account_id, row, "fee_group_not_found"
                )
            if len(group_matches) != 1:
                return _unavailable_fee_schedule(
                    exchange_name, symbol, account_id, row, "fee_group_ambiguous"
                )
            selected_group = group_matches[0]
            selected_group_id = str(selected_group.get("groupId", "")).strip() or None
            native_maker = pick(selected_group, "maker")
            native_taker = pick(selected_group, "taker")
        else:
            maker_fields, taker_fields = _okx_legacy_fee_fields(symbol, asset_type)
            native_maker = pick(row, *maker_fields)
            native_taker = pick(row, *taker_fields)
        if native_maker in (None, "") or native_taker in (None, ""):
            return _unavailable_fee_schedule(
                exchange_name, symbol, account_id, row, "fee_rate_missing"
            )
        raw = {
            "selected_group_id": selected_group_id,
            "maker_native_rate": native_maker,
            "taker_native_rate": native_taker,
        }
        try:
            maker_rate, maker_rebate = _okx_cost_and_rebate(native_maker)
            taker_rate, taker_rebate = _okx_cost_and_rebate(native_taker)
        except ValueError:
            return _unavailable_fee_schedule(
                exchange_name, symbol, account_id, row, "fee_rate_invalid"
            )
        raw.update(
            {
                "maker_rebate_rate": maker_rebate,
                "taker_rebate_rate": taker_rebate,
                "sign_semantics": "okx_negative_commission_positive_rebate",
            }
        )
        if maker_rate is None or taker_rate is None:
            return _unavailable_fee_schedule(
                exchange_name, symbol, account_id, row, "fee_rate_missing"
            )
        return FeeSchedule(
            exchange_name=exchange_name,
            symbol=symbol,
            account_id=account_id,
            maker_rate=maker_rate,
            taker_rate=taker_rate,
            currency=pick(
                row, "currency", "feeCcy", "commissionAsset", "settleCcy", default=metadata_currency
            ),
            source=f"{venue.lower()}_get_fee",
            freshness=_freshness(row),
            raw=raw,
        )

    def read(method, get_exchange_info, exchange_name, symbol, account_id, extra_data, kwargs):
        """Collect OKX fee metadata and request rates for the exact native scope."""
        forbidden = {"inst_id", "inst_family", "group_id", "uly"} & set(kwargs)
        if forbidden:
            raise NormalizedApiError(
                "get_fee_schedule",
                "fee_scope_override_forbidden",
                definite_reject=True,
                category="parameter",
            )
        metadata = get_exchange_info(exchange_name, symbol, extra_data=extra_data, **kwargs)
        scope = okx_fee_scope(metadata, exchange_name, symbol)
        fee_kwargs = {"inst_type": scope["asset_type"], "extra_data": extra_data, **kwargs}
        if scope["asset_type"] in {"SPOT", "MARGIN"}:
            fee_kwargs["inst_id"] = scope["inst_id"]
        elif scope["group_id"] is not None:
            # OKX forbids groupId together with instId/instFamily.
            fee_kwargs["group_id"] = scope["group_id"]
        else:
            fee_kwargs["inst_family"] = scope["inst_family"]
        native = method(**fee_kwargs)
        return fee_schedule(
            native,
            exchange_name,
            symbol,
            account_id,
            expected_group_id=scope["group_id"],
            metadata_currency=scope["currency"],
        )

    return SimpleNamespace(scope=okx_fee_scope, schedule=fee_schedule, read=read)
