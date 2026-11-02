# Experiment Summary

## Environment
- OS: macOS-26.6.2-arm64-arm-64bit
- Python: 3.11.16
- Ollama: 0.32.15
- LLM: `qwen2.5:3b`
- Embeddings: `sentence-transformers/all-MiniLM-L6-v2`
- Hardware: {'model_name': 'MacBook Air', 'model_identifier': 'Mac16,13', 'chip': 'Apple M4', 'cores': '10 (4 Performance and 6 Efficiency)', 'memory': '16 GB'}

## Dataset
- 100 controlled cases: 20 in each of five categories.
- Pilot: 20 cases (first four deterministic cases/category); final: 80 disjoint cases.
- Random seed: 20260824

## Final hyperparameters
- top-k: 3
- alpha/beta: 0.9/0.1
- lambda: 0.08
- threshold: None
- generation: temperature=0.0, top_p=0.9, max_tokens=48, seed=20260824

## Results

| condition | n | precision_mean | precision_std | precision_ci95 | precision_median | precision_p95 | recall_mean | recall_std | recall_ci95 | recall_median | recall_p95 | f1_mean | f1_std | f1_ci95 | f1_median | f1_p95 | recall_at_k_mean | recall_at_k_std | recall_at_k_ci95 | recall_at_k_median | recall_at_k_p95 | correct_mean | correct_std | correct_ci95 | correct_median | correct_p95 | input_tokens_mean | input_tokens_std | input_tokens_ci95 | input_tokens_median | input_tokens_p95 | historical_context_tokens_mean | historical_context_tokens_std | historical_context_tokens_ci95 | historical_context_tokens_median | historical_context_tokens_p95 | memory_tokens_mean | memory_tokens_std | memory_tokens_ci95 | memory_tokens_median | memory_tokens_p95 | context_reduction_vs_full_history_mean | context_reduction_vs_full_history_std | context_reduction_vs_full_history_ci95 | context_reduction_vs_full_history_median | context_reduction_vs_full_history_p95 | embedding_latency_ms_mean | embedding_latency_ms_std | embedding_latency_ms_ci95 | embedding_latency_ms_median | embedding_latency_ms_p95 | retrieval_latency_ms_mean | retrieval_latency_ms_std | retrieval_latency_ms_ci95 | retrieval_latency_ms_median | retrieval_latency_ms_p95 | context_construction_latency_ms_mean | context_construction_latency_ms_std | context_construction_latency_ms_ci95 | context_construction_latency_ms_median | context_construction_latency_ms_p95 | model_latency_ms_mean | model_latency_ms_std | model_latency_ms_ci95 | model_latency_ms_median | model_latency_ms_p95 | total_latency_ms_mean | total_latency_ms_std | total_latency_ms_ci95 | total_latency_ms_median | total_latency_ms_p95 | cross_session_recall |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| full_history | 80 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 0.9500 | 0.2193 | 0.0481 | 1.0000 | 1.0000 | 229.4875 | 26.6306 | 5.8357 | 213.0000 | 273.0500 | 175.4125 | 26.5686 | 5.8221 | 159.5000 | 220.0000 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 0.0000 |  |  | 0.0000 |  |  | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 2.1044 | 0.6324 | 0.1386 | 2.1779 | 2.8928 | 902.0165 | 292.7869 | 64.1597 | 847.0258 | 1450.2066 | 904.2640 | 292.8196 | 64.1669 | 849.3530 | 1452.7197 | 0.8750 |
| recent_context | 80 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 75.6750 | 3.1332 | 0.6866 | 75.0000 | 82.0000 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 0.0000 |  |  | 0.0000 |  |  | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 0.2874 | 0.0387 | 0.0085 | 0.2868 | 0.3697 | 347.6952 | 352.1948 | 77.1781 | 280.1565 | 433.3836 | 348.1165 | 352.2292 | 77.1856 | 280.5366 | 433.7880 | 0.0000 |
| semantic_memory | 80 | 0.4333 | 0.0822 | 0.0180 | 0.5000 | 0.5000 | 1.0000 | 0.0000 | 0.0000 | 1.0000 | 1.0000 | 0.6000 | 0.0822 | 0.0180 | 0.6667 | 0.6667 | 1.0000 | 0.0000 | 0.0000 | 1.0000 | 1.0000 | 0.9500 | 0.2193 | 0.0481 | 1.0000 | 1.0000 | 195.3000 | 22.1390 | 4.8514 | 182.0000 | 228.0500 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 119.4250 | 22.4278 | 4.9147 | 109.0000 | 151.0500 | 0.3218 | 0.0477 | 0.0105 | 0.3395 | 0.3806 | 47.6130 | 18.8994 | 4.1415 | 39.8676 | 83.4907 | 0.1638 | 0.6176 | 0.1353 | 0.1006 | 0.1276 | 1.3685 | 0.3839 | 0.0841 | 1.3770 | 1.9942 | 713.1340 | 284.3082 | 62.3018 | 689.2385 | 1086.6805 | 714.8229 | 284.3833 | 62.3182 | 690.4300 | 1087.9027 | 0.9375 |
| semantic_temporal_memory | 80 | 0.4333 | 0.0822 | 0.0180 | 0.5000 | 0.5000 | 1.0000 | 0.0000 | 0.0000 | 1.0000 | 1.0000 | 0.6000 | 0.0822 | 0.0180 | 0.6667 | 0.6667 | 1.0000 | 0.0000 | 0.0000 | 1.0000 | 1.0000 | 0.9500 | 0.2193 | 0.0481 | 1.0000 | 1.0000 | 195.3000 | 22.1390 | 4.8514 | 182.0000 | 228.0500 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 119.4250 | 22.4278 | 4.9147 | 109.0000 | 151.0500 | 0.3218 | 0.0477 | 0.0105 | 0.3395 | 0.3806 | 47.6130 | 18.8994 | 4.1415 | 39.8676 | 83.4907 | 0.1508 | 0.0476 | 0.0104 | 0.1645 | 0.2145 | 1.3711 | 0.4151 | 0.0910 | 1.4109 | 1.8901 | 302.3844 | 281.1240 | 61.6040 | 238.2860 | 769.6763 | 304.0606 | 281.1704 | 61.6142 | 240.1153 | 771.5571 | 0.9375 |

## Failure analysis

| condition | failure_type | count | percentage_of_condition |
| --- | --- | --- | --- |
| full_history | correct history supplied but answer incorrect | 4 | 5.0000 |
| recent_context | cross-session recall failure | 16 | 20.0000 |
| recent_context | target outside recent context | 64 | 80.0000 |
| semantic_memory | correct memory retrieved but answer incorrect | 4 | 5.0000 |
| semantic_temporal_memory | correct memory retrieved but answer incorrect | 4 | 5.0000 |

## Key observations
- Response accuracy was 0.000 for recent context, 0.950 for full history, and 0.950 for both retrieval conditions.
- Both retrieval conditions achieved recall 1.000 and F1 0.600; temporal re-ranking produced no measured retrieval or response advantage in this final set.
- Retrieved-memory tokens were 32.2% lower than full-history historical tokens while matching full-history accuracy.
- Cross-session response recall was 0.000, 0.875, and 0.938 for each retrieval method.
- The retrieval-versus-recent paired accuracy difference had p < 0.05 under the predeclared exact McNemar/binomial test; retrieval versus full history was not significant (see `paired_tests.csv`).
- Retrieval metrics apply only to retrieval-enabled conditions; baseline zeros mean retrieval was not performed.

## Limitations
- Synthetic controlled data; one local LLM and one embedding model; 80-case final set.
- Latency is hardware- and load-specific; generation may retain limited backend nondeterminism.
- Conditions ran in a fixed order, so model warm-up/cache effects confound between-condition generation and total-latency comparisons.
- Deterministic substring/variant scoring can miss semantically correct paraphrases or accept verbose answers containing the target.
