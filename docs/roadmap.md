# Meaningful backlog

1. **Official dataset integration** — validate loaders on the licensed cleaned LongMemEval and LoCoMo releases; record hashes and test abstention/category counts. Acceptance: no gold leakage; official output schemas; documented exclusions.
2. **Mem0 reproduction** — finish provider/store config for pinned Mem0; retain infer=True; isolate/reset state and measure extraction calls. Acceptance: runnable matched-model baseline, full config and traces without private data.
3. **Privacy evaluation** — connect the explicit policy to the existing retrieval pipeline and author independent privacy labels. Acceptance: retain/update/reject/forget tests plus allowed recall and violation metrics for constrained/unconstrained arms.
4. **Fair evaluation and uncertainty** — preregister primary comparisons; randomize/counterbalance condition order; record actual prompt/output/adjudication tokens and full pipeline timing. Acceptance: paired case/cluster uncertainty, median/p95 with counts, no deterministic pseudo-replication, actual or clearly estimated costs.
5. **Publication rights** — confirm original code/data ownership, research authors and license scope. Acceptance: recorded owner decision; no private conversations or restricted data; final tree and history scan.
