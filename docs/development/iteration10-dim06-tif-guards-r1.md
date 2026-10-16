# Iteration 10 DIM06 OKX market/post-only guard (R1)

Date: 2026-10-16. Repository: bt_api/bt_api_okx, branch dev, baseline HEAD 8c0019db377141664513908b8ff4071643369fd5.

This narrow round rejects market + post_only in src/bt_api_okx/feeds/live_okx/mixins/trade_mixin.py at the local order boundary, before symbol conversion/request preparation. Limit + post-only (GTC) and market without post-only remain supported neighbors.

Root's fixed-source joint SDK check included this package's canonical production imports and terminal synthetic request spy: 21 cases passed in 1.36s, Python/pytest exit 0, no warnings, empty stderr, 221 source pins unchanged, and the four bound repository HEADs unchanged. The node breakdown is 8 supported Binance TIF parameterizations, 9 local rejects, one market omission, one valid native GTD case, one OKX rejection, and one OKX valid-neighbor case. Evidence is under dim06-tif-guards-20261016; the preserved spec.json retains its creation-time UNEXECUTED evidence-level field, while result.json and stdout.log record the completed run.

Evidence is synthetic/local only. No exchange, account, credentials, or real provider request was used. This package change can be committed independently as the exact two-path scope below; no package-local test or separate QA was run.

- src/bt_api_okx/feeds/live_okx/mixins/trade_mixin.py — SHA-256 9241d5d9dac48ab75eee9fb03234259aed8bf9a7a18c72506f4e6997bc6859c9
- docs/development/iteration10-dim06-tif-guards-r1.md — this round record
- Proposed commit subject: fix(okx): reject market post-only orders locally
- Commit status: not committed; Root should recheck the scoped diff and stage only these two paths.