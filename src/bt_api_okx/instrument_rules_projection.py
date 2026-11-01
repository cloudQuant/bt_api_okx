"""OKX native instrument-rule projection."""


def project_instrument_rules(row, *, pick, normalized_error):
    NormalizedApiError = normalized_error
    filters = {
        item.get("filterType"): item for item in row.get("filters", []) if isinstance(item, dict)
    }
    lot = filters.get("LOT_SIZE") or filters.get("MARKET_LOT_SIZE") or {}
    price_filter = filters.get("PRICE_FILTER") or {}
    notional_filter = filters.get("MIN_NOTIONAL") or filters.get("NOTIONAL") or {}
    required = {
        "contract_value": pick(row, "ctVal", "contract_value"),
        "contract_multiplier": pick(row, "ctMult", "contract_multiplier", default="1"),
        "price_tick": pick(row, "tickSz", "price_tick"),
        "quantity_step": pick(row, "lotSz", "quantity_step"),
        "min_quantity": pick(row, "minSz", "min_quantity"),
    }
    max_quantity_raw = pick(row, "max_quantity", "maxLmtSz", "maxMktSz")
    quantity_unit = "contracts"
    return (required, max_quantity_raw, quantity_unit, notional_filter, True)
