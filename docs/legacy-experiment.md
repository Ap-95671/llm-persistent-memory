# Persistent Memory and Context Management in Large Language Models

This standalone Python research project compares four ways of supplying conversational history to the same local LLM: recent context, deterministic full history, semantic persistent-memory retrieval, and semantic-plus-temporal retrieval. It is isolated from application repositories and produces auditable raw data rather than pre-filled results.

## Experimental controls

Every condition uses `qwen2.5:3b`, the same system instruction, query, 8,192-token context setting, temperature 0, top-p 0.9, 48-token output limit, and seed 20260824. The independent variable is the historical-information strategy. Recent context is exactly the final two prior messages. Full history keeps the newest complete messages that fit a 7,000-token history budget. Memory conditions present labelled retrieved memories, then the same two recent messages, then the query.

Semantic retrieval uses normalized `sentence-transformers/all-MiniLM-L6-v2` vectors and FAISS inner product (cosine similarity). Temporal retrieval maps cosine similarity from `[-1,1]` to `[0,1]`, computes `exp(-lambda * age_in_days)`, and combines the scores with pilot-selected alpha and beta. The threshold is disabled unless explicitly configured.

## Project layout

- `config.py`: fixed models, seeds, generation controls, budgets, and pilot grid.
- `src/`: dataset, embeddings, FAISS store, retrieval, context, model client, metrics, and reporting.
- `experiments/`: pilot selection and final evaluation orchestration.
- `data/`: all 100 cases plus disjoint pilot/final files.
- `results/`: canonical measured tables, metadata, statistical tests, and summary.
- `runs/<UTC timestamp>/`: preserved raw results and configuration for each completed final run.
- `figures/`: publication-oriented PNG/PDF figures.
- `tests/`: deterministic sanity tests.

## Installation and Ollama setup

On Apple Silicon with Homebrew:

```bash
brew install python@3.11 ollama
brew services start ollama
ollama pull qwen2.5:3b
cd /path/to/llm-memory-experiment
/opt/homebrew/bin/python3.11 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
```

On other systems, install Python 3.11+, follow the official Ollama installation instructions, start `ollama serve`, and use the same `ollama pull` command. Do not substitute another model if reproducing this experiment.

The first pilot run downloads the MiniLM embedding files from Hugging Face; the final run downloads only the Qwen tokenizer files for input-token measurement. Model weights for Qwen remain in Ollama.

## Reproducing the Experiment

The virtual environment and local Hugging Face caches are reproducible artifacts and do not need to be archived. On Apple Silicon, recreate them and rerun the experiment with:

```bash
cd /path/to/llm-memory-experiment

brew install python@3.11 ollama
brew services start ollama
ollama pull qwen2.5:3b

/opt/homebrew/bin/python3.11 -m venv .venv
.venv/bin/python -m pip install --upgrade pip
.venv/bin/python -m pip install -r requirements.txt

source .venv/bin/activate
python run_experiment.py dataset
python -m pytest -q
python run_experiment.py pilot
python run_experiment.py final
```

On non-Homebrew systems, install Python 3.11 or newer and Ollama using the platform-specific installer, then run the same `ollama pull`, virtual-environment, dependency-installation, and experiment commands. The pilot run automatically re-downloads `sentence-transformers/all-MiniLM-L6-v2`; the final run automatically re-downloads the `Qwen/Qwen2.5-3B-Instruct` tokenizer. The Qwen generation model is supplied exclusively by Ollama as `qwen2.5:3b`.

Or run dataset generation, pilot selection, and final evaluation together after tests:

```bash
source .venv/bin/activate
python run_experiment.py all
```

Dataset generation is deterministic. The first four generated cases in each category are assigned to pilot tuning before any evaluation (20 total); the remaining 80 form the untouched final set. The pilot compares k = 3, 5, and 10 and alpha/beta pairs 0.9/0.1 through 0.5/0.5. It maximizes the mean retrieval F1 of the semantic and temporal strategies, breaking ties by smaller k and then larger alpha. It writes `results/parameter_selection.csv` and freezes the choice in `results/frozen_parameters.json` before final inference.

## Outputs and interpretation

`raw_results.csv` and `.json` contain one row/record per final case and condition (320 total), including answers, ground truth, retrieved IDs, scoring, tokens, truncation, and component latencies. `aggregate_results.csv` and `per_category_results.csv` include n, mean, sample standard deviation, median, p95, and 95% normal-approximation confidence-interval half-widths. `paired_tests.csv` records exact McNemar/binomial tests for paired response accuracy; significance is not asserted automatically beyond the recorded p-value and alpha. `failure_analysis.csv` contains rule-based failure types.

Figures are regenerated automatically during a final run as PNG and PDF: retrieval F1, response accuracy, cross-session recall, input-token usage, and retrieval latency. `results/experiment_summary.md` captures the actual environment, frozen parameters, results, failures, observations, and limitations.

Latency uses `time.perf_counter`. Embedding, FAISS search, context construction, Ollama inference, and total interaction time are separated. Input tokens are counted with the Hugging Face tokenizer matching Qwen2.5. Context reduction is `1 - memory_tokens/full_history_historical_tokens`; it must be interpreted alongside accuracy.

Completed runs are preserved under a new UTC timestamp directory. The canonical `results/` tables point to the most recent completed run, while the timestamped raw results and frozen configuration retain prior evidence.

## Dataset validation and leakage controls

Generation validates 100 total cases, exactly 20 per category, unique memory IDs, non-empty queries/answers, resolvable ground-truth IDs, ordered timestamps, and genuine old/new pairs. The pilot and final IDs are disjoint. In every case, the ground-truth target is outside the two-turn recent window. Memory indexes contain only history preceding that recent window; neither expected answers nor ground-truth labels enter prompts.

## Known limitations

The study uses controlled synthetic conversations, one LLM, one embedding model, and 80 final cases. Deterministic answer matching is transparent but imperfect for paraphrases. Local hardware and background load affect latency. Ollama seed and temperature reduce variance but do not guarantee bit-for-bit determinism on every backend/version.
