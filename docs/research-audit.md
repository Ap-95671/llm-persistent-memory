# Evidence and research status

Audited 2 November 2026. Original files were read before copying; the original folder is unchanged. The enclosing original Git repository has no commits, so there was no research commit history to transplant. An external SHA-256 inventory records the original files. The original source, data, raw outputs, timestamped run and figures are preserved. The former README is `legacy-experiment.md`.

| Component | Classification | Evidence / boundary |
| --- | --- | --- |
| Synthetic dataset and four retrieval/context strategies | Implemented and verified in unit tests | Existing code; 100 generated cases, 20 pilot / 80 final |
| Original model-generated answers and latency | Implemented but not independently reproduced | Preserved 320 records; model inference has not been rerun |
| Recomputed score consistency, paired intervals | Implemented and verified | `tools/audit_preserved_results.py`, `results/reanalysis.json` |
| Explicit-label policy and SQLite persistence | Experimental; unit tested | `pmemory/`; new work, separate from historical experiment |
| Automatic extraction, sensitivity/consent inference | Planned | No trained classifier, extractor or consent inference exists |
| LongMemEval / LoCoMo schema loaders | Implemented and verified on authored fixtures | Real dataset validation and inference pending |
| Mem0 baseline | Experimental interface only | Upstream version pinned; live construction/configuration/inference pending |
| Privacy improves answers / retention | Missing evidence | No comparative experiment exists |
| Formal privacy, secure erasure, hardware validation | Missing evidence | Not claimed |

The historical recent-context baseline was not weakened after seeing outcomes: its pre-existing definition uses two turns. Nevertheless, **all gold targets deliberately occur earlier**, so a zero score is an unsuitable general superiority argument. Full-history accuracy is the stronger existing comparison. The longest synthetic histories are only a few messages; these are not long-context evaluations.

The 0.60 retrieval F1 needs additional caution: stable/cross/temporal cases have only two eligible memories with k=3, updated cases three, and distractor cases four. High recall on this tiny candidate set does not establish scalable retrieval quality.

The old `total_latency_ms` excludes embedding and store construction performed before the condition loop. Do not call it complete end-to-end latency. Conditions ran in fixed order, so cache/warm-up differences prevent causal latency comparisons. Historical normal intervals are retained for provenance, not endorsed as calibrated binary confidence bounds. The new Wilson intervals are bounded; paired bootstrap resamples cases, never repeated deterministic calls. Templated/nonrandom data limits their inferential meaning.

## Preparation environment correction

The added SciPy 1.15.2 wheel failed to load on the preparation Mac when testing historical statistics. SciPy is now pinned to 1.16.3, whose exact-binomial function and historical paired results were verified locally. This is a reproduction-environment change, not a change to the preserved historical measurements or recorded original environment.
