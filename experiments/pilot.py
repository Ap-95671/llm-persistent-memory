from __future__ import annotations

from datetime import datetime, timedelta
from pathlib import Path

import pandas as pd

from config import CONFIG
from src.embeddings import EmbeddingModel
from src.evaluation import retrieval_metrics
from src.memory_store import MemoryStore
from src.retrieval import semantic_retrieve, temporal_retrieve
from src.utils import read_json, write_json


def run_pilot(project: Path, embedder: EmbeddingModel) -> tuple[pd.DataFrame, dict]:
    cases = read_json(project/"data/pilot_cases.json")["cases"]
    detail=[]
    for case in cases:
        eligible=case["history"][:-CONFIG.recent_turn_limit]
        vectors, embedding_ms=embedder.encode([m["text"] for m in eligible]+[case["evaluation_query"]])
        store=MemoryStore(eligible,vectors[:-1]); query_vec=vectors[-1]
        query_time=datetime.fromisoformat(case["history"][-1]["timestamp"])+timedelta(days=1)
        for k in CONFIG.pilot_k_values:
            hits,lat=semantic_retrieve(store,query_vec,k,CONFIG.relevance_threshold)
            detail.append({"case_id":case["id"],"category":case["category"],"strategy":"semantic","k":k,"alpha":1.0,"beta":0.0,"threshold":CONFIG.relevance_threshold,"embedding_latency_ms":embedding_ms,"retrieval_latency_ms":lat,**retrieval_metrics([h["id"] for h in hits],case["ground_truth_memory_ids"])})
            for alpha in CONFIG.pilot_alpha_values:
                beta=round(1-alpha,10)
                hits,lat=temporal_retrieve(store,query_vec,k,alpha,beta,CONFIG.temporal_lambda,query_time,CONFIG.relevance_threshold)
                detail.append({"case_id":case["id"],"category":case["category"],"strategy":"semantic_temporal","k":k,"alpha":alpha,"beta":beta,"threshold":CONFIG.relevance_threshold,"embedding_latency_ms":embedding_ms,"retrieval_latency_ms":lat,**retrieval_metrics([h["id"] for h in hits],case["ground_truth_memory_ids"])})
    detail_df=pd.DataFrame(detail)
    summary=detail_df.groupby(["strategy","k","alpha","beta","threshold"],dropna=False).agg(n=("case_id","size"),precision=("precision","mean"),recall=("recall","mean"),f1=("f1","mean"),recall_at_k=("recall_at_k","mean"),retrieval_latency_ms=("retrieval_latency_ms","mean")).reset_index()
    candidates=[]
    sem=summary[summary.strategy=="semantic"].set_index("k")
    for _,row in summary[summary.strategy=="semantic_temporal"].iterrows():
        candidates.append({"k":int(row.k),"alpha":float(row.alpha),"beta":float(row.beta),"semantic_f1":float(sem.loc[row.k,"f1"]),"temporal_f1":float(row.f1),"selection_score":float((sem.loc[row.k,"f1"]+row.f1)/2)})
    candidates=pd.DataFrame(candidates).sort_values(["selection_score","k","alpha"],ascending=[False,True,False])
    chosen=candidates.iloc[0].to_dict(); chosen |= {"lambda":CONFIG.temporal_lambda,"threshold":CONFIG.relevance_threshold,"selection_rule":"maximize mean pilot retrieval F1 across semantic and semantic-temporal strategies; tie-break by smaller k then larger alpha","pilot_case_count":len(cases)}
    summary["selected"]=(summary.k==chosen["k"]) & (((summary.strategy=="semantic") & (summary.alpha==1.0)) | ((summary.strategy=="semantic_temporal") & (summary.alpha==chosen["alpha"])))
    summary.to_csv(project/"results/parameter_selection.csv",index=False)
    detail_df.to_csv(project/"results/pilot_raw_results.csv",index=False)
    write_json(project/"results/frozen_parameters.json",chosen)
    return summary,chosen

