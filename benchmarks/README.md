# Benchmark setup and evaluation boundaries

Upstream files were inspected at the exact commits in `upstream-lock.json`, including licenses and scoring code. Data is not bundled. Put downloads in ignored `external-data/`; record exact URL, release and SHA-256 in every experiment manifest. Current adapters only load text and separate gold references from model inputs; they do not generate answers or official scores.

## LongMemEval

[Official repository](https://github.com/xiaowu0162/LongMemEval), [paper](https://arxiv.org/abs/2410.10813), [cleaned dataset](https://huggingface.co/datasets/xiaowu0162/longmemeval-cleaned). The upstream README now recommends cleaned S/M files; the older Hugging Face dataset is deprecated. The inspected code LICENSE is MIT; the older dataset card declares MIT. Confirm the cleaned dataset's own current license/card before using or distributing it; the lock does not grant data rights. No data redistribution is planned here.

LongMemEval evaluates extraction, multisession reasoning, updates, temporal reasoning and abstention. Keep all role-labelled timestamped sessions, not just gold evidence. The oracle subset supplies evidence sessions and must be labelled oracle, not a full-history result. Upstream retrieval scoring excludes abstention questions because they lack gold locations; QA includes them. Export model answers as JSONL `{question_id, hypothesis}`. Use the pinned upstream `src/evaluation/evaluate_qa.py` and category-specific prompts. The inspected GPT-4o judge resolves to `gpt-4o-2024-08-06`; executing it incurs paid calls and requires authorization. Do not replace it with the synthetic substring scorer and call that official accuracy.

```bash
python -m benchmarks.adapters longmemeval external-data/longmemeval_s_cleaned.json
# After authorized model inference and paid judge approval, from a pinned upstream clone:
# python src/evaluation/evaluate_qa.py gpt-4o hypotheses.jsonl external-data/longmemeval_s_cleaned.json
```

## LoCoMo

[Official repository](https://github.com/snap-research/locomo), [paper](https://aclanthology.org/2024.acl-long.747/), [dataset path](https://github.com/snap-research/locomo/blob/main/data/locomo10.json), [license](https://github.com/snap-research/locomo/blob/main/LICENSE.txt). The inspected release is CC BY-NC 4.0; do not treat it as commercial-use permission. The ten conversation samples carry multiple correlated QA annotations. Text-only adapters preserve speaker identity, ordered sessions and dates; images/captions, summaries and generated observations are not ingested. Text-only limitations must be reported.

The official `task_eval/evaluation.py` uses category-specific stemmed token F1/subanswer handling, and separate adversarial-category logic. Preserve those rules and report categories rather than treating LongMemEval judge accuracy and LoCoMo F1 as one metric. No upstream evaluator is copied or replaced here. Use official `task_eval/evaluate_qa.py` with its documented model/output settings after approval; preserve its prediction field convention. Inference and scoring are pending.

```bash
python -m benchmarks.adapters locomo external-data/locomo10.json
```

Use conversation-level cluster resampling for LoCoMo uncertainty (only ten clusters; intervals may be unstable), and paired question/case designs for LongMemEval with dependence disclosed. Do not count each question in a shared LoCoMo conversation as an independent sample.

## Baselines and controls

- **No memory:** same reader/system instruction/question/output settings; last two prior turns, no external retrieval. Enforce the same overall token budget. Also report a full-history baseline with deterministic truncation; memory gains over the two-turn baseline alone are not sufficient.
- **Mem0:** inspected source identifies `mem0ai==2.2.1`, Apache-2.0. Optional dependency in `requirements-mem0.txt`; `Mem0Baseline` preserves default `infer=True`, user isolation and `search(limit=...)`. Do not replace it with vector lookup alone. A fully specified reader/embedder/store configuration, disabled telemetry, state reset per conversation, API call accounting and live reproduction remain pending. No Mem0 score is reported.
- **Proposed:** privacy adjudication prototype, not yet wired to reader/retriever evaluation. Unconstrained ablation must hold the extractor, retriever, reader and budgets fixed. Report additional adjudication/extraction calls in cost and end-to-end timing.

Freeze prompts, model digests, tokenizer/embedding revisions, splits, seeds, budgets, temperature, top-p, concurrency, runtime and hardware. Present chronological input without answer/evidence labels. Record truncation and excluded-question counts. A model tag is not an immutable digest; existing runs did not capture one. `configs/evaluation.json` marks unresolved fields explicitly. Paid execution is disabled by procedure: these loaders make no model calls.
