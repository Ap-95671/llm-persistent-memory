from __future__ import annotations

import json
from datetime import datetime, timedelta
from pathlib import Path
from time import perf_counter

import pandas as pd

from config import CONFIG
from src.context_builder import TokenCounter, build_context
from src.embeddings import EmbeddingModel
from src.evaluation import answer_correct, classify_failure, retrieval_metrics
from src.llm import OllamaLLM
from src.memory_store import MemoryStore
from src.retrieval import semantic_retrieve, temporal_retrieve
from src.utils import read_json

CONDITIONS=["recent_context","full_history","semantic_memory","semantic_temporal_memory"]


def run_final(project:Path,embedder:EmbeddingModel,counter:TokenCounter,llm:OllamaLLM,params:dict)->pd.DataFrame:
    cases=read_json(project/"data/final_cases.json")["cases"]; rows=[]
    system_tokens=counter.count(CONFIG.system_prompt)
    for case_index,case in enumerate(cases,1):
        eligible=case["history"][:-CONFIG.recent_turn_limit]
        vectors,embed_ms=embedder.encode([m["text"] for m in eligible]+[case["evaluation_query"]])
        store=MemoryStore(eligible,vectors[:-1]); qvec=vectors[-1]
        query_time=datetime.fromisoformat(case["history"][-1]["timestamp"])+timedelta(days=1)
        for condition in CONDITIONS:
            interaction_start=perf_counter(); retrieved=[]; retrieval_ms=0.0
            if condition=="semantic_memory": retrieved,retrieval_ms=semantic_retrieve(store,qvec,int(params["k"]),params.get("threshold"))
            elif condition=="semantic_temporal_memory": retrieved,retrieval_ms=temporal_retrieve(store,qvec,int(params["k"]),float(params["alpha"]),float(params["beta"]),float(params["lambda"]),query_time,params.get("threshold"))
            prompt,context_metrics=build_context(condition,case,retrieved,counter,CONFIG.recent_turn_limit,CONFIG.full_history_token_budget)
            answer,model_ms,model_meta=llm.generate(prompt)
            retrieved_ids=[m["id"] for m in retrieved]
            retrieval_eval=retrieval_metrics(retrieved_ids,case["ground_truth_memory_ids"]) if condition.startswith("semantic") else {"precision":0.0,"recall":0.0,"f1":0.0,"recall_at_k":0.0}
            row={"case_id":case["id"],"category":case["category"],"condition":condition,"query":case["evaluation_query"],"expected_answer":case["expected_answer"],"generated_answer":answer,"correct":answer_correct(answer,case["expected_answer"],case.get("acceptable_answers",[])),"ground_truth_memory_ids":case["ground_truth_memory_ids"],"retrieved_memory_ids":retrieved_ids,"top_k":int(params["k"]) if condition.startswith("semantic") else None,"semantic_weight":1.0 if condition=="semantic_memory" else (float(params["alpha"]) if condition=="semantic_temporal_memory" else None),"temporal_weight":float(params["beta"]) if condition=="semantic_temporal_memory" else None,"embedding_latency_ms":embed_ms if condition.startswith("semantic") else 0.0,"retrieval_latency_ms":retrieval_ms,"model_latency_ms":model_ms,"total_latency_ms":(perf_counter()-interaction_start)*1000,"input_tokens":system_tokens+context_metrics["prompt_tokens"],"model_prompt_eval_count":model_meta.get("prompt_eval_count"),"model_eval_count":model_meta.get("eval_count"),**retrieval_eval,**context_metrics}
            row["failure_type"]=classify_failure(row,case); rows.append(row)
        print(f"Completed final case {case_index}/{len(cases)}: {case['id']}",flush=True)
    return pd.DataFrame(rows)


def serialize_lists(df:pd.DataFrame)->pd.DataFrame:
    out=df.copy()
    for column in ["ground_truth_memory_ids","retrieved_memory_ids","full_history_memory_ids"]:
        out[column]=out[column].map(json.dumps)
    return out

