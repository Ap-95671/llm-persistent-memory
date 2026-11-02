from __future__ import annotations

import math
from collections import Counter

import numpy as np
import pandas as pd

from src.utils import normalize_text


def retrieval_metrics(retrieved: list[str], ground: list[str]) -> dict:
    r, g = set(retrieved), set(ground); overlap = len(r & g)
    precision = overlap / len(r) if r else (1.0 if not g else 0.0)
    recall = overlap / len(g) if g else 1.0
    f1 = 2*precision*recall/(precision+recall) if precision+recall else 0.0
    return {"precision":precision,"recall":recall,"f1":f1,"recall_at_k":recall}


def answer_correct(answer: str, expected: str, variants: list[str]) -> bool:
    actual = normalize_text(answer)
    if not actual: return False
    for candidate in [expected, *variants]:
        target = normalize_text(candidate)
        if actual == target or (target and target in actual): return True
    return False


def classify_failure(row: dict, case: dict) -> str:
    if row["correct"]: return "none"
    retrieved = set(row["retrieved_memory_ids"]); ground = set(case["ground_truth_memory_ids"])
    if row["condition"] == "full_history":
        if row.get("full_history_truncated") and not ground.intersection(row.get("full_history_memory_ids", [])): return "full-history truncation failure"
        return "correct history supplied but answer incorrect"
    if row["condition"] == "recent_context":
        return "cross-session recall failure" if case["category"] == "cross_session" else "target outside recent context"
    if retrieved.intersection(set(case.get("superseded_memory_ids", []))) and not retrieved.intersection(ground): return "outdated memory retrieved"
    if case["category"] == "temporal" and not ground.intersection(retrieved): return "temporal-ranking failure"
    if case["category"] == "distractor" and retrieved.intersection(set(case.get("distractor_memory_ids", []))): return "distractor interference"
    if ground.intersection(retrieved): return "correct memory retrieved but answer incorrect"
    return "relevant memory not retrieved"


def ci95(values: pd.Series) -> float:
    clean = values.dropna().astype(float)
    return 1.96 * clean.std(ddof=1) / math.sqrt(len(clean)) if len(clean) > 1 else 0.0


def aggregate(df: pd.DataFrame, groups: list[str]) -> pd.DataFrame:
    metrics = ["precision","recall","f1","recall_at_k","correct","input_tokens","historical_context_tokens","memory_tokens","context_reduction_vs_full_history","embedding_latency_ms","retrieval_latency_ms","context_construction_latency_ms","model_latency_ms","total_latency_ms"]
    rows=[]
    for keys, part in df.groupby(groups, dropna=False):
        if not isinstance(keys, tuple): keys=(keys,)
        row=dict(zip(groups,keys)); row["n"]=len(part)
        for metric in metrics:
            vals=part[metric].astype(float); clean=vals.dropna()
            row[f"{metric}_mean"]=clean.mean() if len(clean) else np.nan; row[f"{metric}_std"]=clean.std(ddof=1) if len(clean)>1 else (0.0 if len(clean)==1 else np.nan); row[f"{metric}_ci95"]=ci95(clean); row[f"{metric}_median"]=clean.median() if len(clean) else np.nan; row[f"{metric}_p95"]=np.percentile(clean,95) if len(clean) else np.nan
        cross=part[part.category=="cross_session"]
        row["cross_session_recall"]=cross["correct"].mean() if len(cross) else np.nan
        rows.append(row)
    return pd.DataFrame(rows)
