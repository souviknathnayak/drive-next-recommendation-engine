# Evaluation protocol

Run `py -m unittest discover -s tests -v` before every release. A production gate should add representative, consented holdout data and use versioned thresholds:

| Measure | Suggested launch gate | Why |
|---|---:|---|
| Catalog grounding | 100% | Recommendations must be real, available products. |
| Hallucination proxy | 0 failed grounding checks | Reject unsupported product claims. |
| Cohort parity gap | <= 0.15 (investigate any gap) | Screening for disparate recommendation rates. |
| Adversarial pass rate | 100% critical cases | Block injection and protected-trait steering. |
| p95 latency | product-defined SLO | Prevent degraded interaction quality. |
| Token budget | product-defined cap | Control cost and agent runaway behaviour. |

The built-in adversarial cases cover: protected-field stripping, catalog-only output, an intent-shift question, and a disparate-outcome audit. Expand with multilingual prompts, sensitive product categories, indirect proxy attributes, malformed inputs, tool-result poisoning, and negative/abusive user content. Pair aggregate parity checks with qualitative review; no single fairness metric establishes absence of bias.
