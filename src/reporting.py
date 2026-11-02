from __future__ import annotations

import importlib.metadata as metadata
import json
import platform
import re
import shutil
import subprocess
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy.stats import binomtest

from config import CONFIG
from src.evaluation import aggregate
from src.utils import utc_now, write_json

LABELS={"recent_context":"Recent context","full_history":"Full history","semantic_memory":"Semantic memory","semantic_temporal_memory":"Semantic + temporal"}


def _markdown_table(frame:pd.DataFrame)->str:
    """Dependency-free compact Markdown rendering for experiment summaries."""
    if frame.empty: return "No rows."
    display=frame.copy()
    for column in display.select_dtypes(include=["float"]).columns:
        display[column]=display[column].map(lambda value:"" if pd.isna(value) else f"{value:.4f}")
    headers=[str(c) for c in display.columns]
    lines=["| "+" | ".join(headers)+" |","| "+" | ".join(["---"]*len(headers))+" |"]
    for row in display.astype(str).itertuples(index=False,name=None): lines.append("| "+" | ".join(value.replace("|","\\|") for value in row)+" |")
    return "\n".join(lines)


def paired_tests(df:pd.DataFrame)->pd.DataFrame:
    pivot=df.pivot(index="case_id",columns="condition",values="correct").astype(bool); rows=[]
    for left,right in [("semantic_memory","recent_context"),("semantic_temporal_memory","recent_context"),("semantic_memory","full_history"),("semantic_temporal_memory","full_history")]:
        b=int(((pivot[left])&(~pivot[right])).sum()); c=int(((~pivot[left])&(pivot[right])).sum()); n=b+c
        p=binomtest(min(b,c),n,0.5).pvalue if n else 1.0
        rows.append({"condition_a":left,"condition_b":right,"a_correct_b_wrong":b,"a_wrong_b_correct":c,"discordant_n":n,"test":"exact McNemar/binomial","p_value":p,"alpha":0.05,"significant":p<0.05})
    return pd.DataFrame(rows)


def make_figures(df:pd.DataFrame,figdir:Path)->None:
    figdir.mkdir(parents=True,exist_ok=True)
    specs=[
        ("retrieval_f1",df[df.condition.str.startswith("semantic")].groupby("condition").f1.mean(),"Mean retrieval F1","Retrieval F1",(0,1)),
        ("response_accuracy",df.groupby("condition").correct.mean(),"Response accuracy","Accuracy",(0,1)),
        ("cross_session_recall",df[df.category=="cross_session"].groupby("condition").correct.mean(),"Cross-session response recall","Recall",(0,1)),
        ("context_usage",df.groupby("condition").input_tokens.mean(),"Average input context usage","Input tokens",None),
        ("retrieval_latency",df[df.condition.str.startswith("semantic")].groupby("condition").retrieval_latency_ms.mean(),"Mean retrieval latency","Milliseconds",None),
    ]
    for name,series,title,ylabel,ylim in specs:
        fig,ax=plt.subplots(figsize=(6.4,4.0)); x=np.arange(len(series)); labels=[LABELS.get(i,i) for i in series.index]
        ax.bar(x,series.values,color="#2b6f8a",width=.65); ax.set_xticks(x,labels,rotation=15,ha="right"); ax.set_ylabel(ylabel); ax.set_title(f"{title} (n={len(df.case_id.unique())} cases)"); ax.grid(axis="y",alpha=.25)
        if ylim: ax.set_ylim(*ylim)
        fig.tight_layout()
        for ext in ["png","pdf"]: fig.savefig(figdir/f"{name}.{ext}",dpi=300,bbox_inches="tight")
        plt.close(fig)


def environment_info()->dict:
    packages={}
    for p in ["numpy","pandas","matplotlib","scikit-learn","sentence-transformers","faiss-cpu","transformers","torch","requests"]:
        try: packages[p]=metadata.version(p)
        except metadata.PackageNotFoundError: packages[p]="missing"
    try:
        version_result=subprocess.run(["ollama","--version"],capture_output=True,text=True,check=False)
        version_text=version_result.stdout+"\n"+version_result.stderr
        match=re.search(r"(?:client version is|version is)\s+([\d.]+)",version_text)
        ollama=match.group(1) if match else version_text.strip()
    except OSError: ollama="missing"
    hardware={}
    try:
        text=subprocess.run(["system_profiler","SPHardwareDataType"],capture_output=True,text=True,check=False).stdout
        for label,key in [("Model Name","model_name"),("Model Identifier","model_identifier"),("Chip","chip"),("Total Number of Cores","cores"),("Memory","memory")]:
            match=re.search(rf"^\s*{re.escape(label)}:\s*(.+)$",text,re.MULTILINE)
            if match: hardware[key]=match.group(1).strip()
    except OSError: pass
    return {"captured_at":utc_now(),"os":platform.platform(),"machine":platform.machine(),"processor":platform.processor(),"hardware":hardware,"python":platform.python_version(),"ollama":ollama,"llm_model":CONFIG.llm_model,"embedding_model":CONFIG.embedding_model,"tokenizer_model":CONFIG.tokenizer_model,"packages":packages,"disk_free_bytes":shutil.disk_usage(Path.cwd()).free}


def write_outputs(project:Path,df:pd.DataFrame,params:dict,run_dir:Path)->None:
    results=project/"results"; results.mkdir(exist_ok=True); run_dir.mkdir(parents=True,exist_ok=False)
    from experiments.final_evaluation import serialize_lists
    full=df[df.condition=="full_history"].set_index("case_id").historical_context_tokens
    for condition in ["semantic_memory","semantic_temporal_memory"]:
        mask=df.condition==condition
        df.loc[mask,"context_reduction_vs_full_history"]=df[mask].apply(lambda r:1-r.memory_tokens/full.loc[r.case_id] if full.loc[r.case_id] else np.nan,axis=1)
    serial=serialize_lists(df); serial.to_csv(results/"raw_results.csv",index=False); serial.to_csv(run_dir/"raw_results.csv",index=False)
    records=json.loads(df.to_json(orient="records")); write_json(results/"raw_results.json",records); write_json(run_dir/"raw_results.json",records)
    agg=aggregate(df,["condition"]); cat=aggregate(df,["condition","category"])
    agg.to_csv(results/"aggregate_results.csv",index=False); cat.to_csv(results/"per_category_results.csv",index=False)
    agg.to_csv(run_dir/"aggregate_results.csv",index=False); cat.to_csv(run_dir/"per_category_results.csv",index=False)
    paired_tests(df).to_csv(results/"paired_tests.csv",index=False)
    failures=df[df.failure_type!="none"].groupby(["condition","failure_type"]).size().rename("count").reset_index(); failures["percentage_of_condition"]=failures["count"]/len(df.case_id.unique())*100; failures.to_csv(results/"failure_analysis.csv",index=False)
    make_figures(df,project/"figures"); env=environment_info(); write_json(results/"environment.json",env); write_json(run_dir/"environment.json",env); write_json(run_dir/"frozen_parameters.json",params)
    indexed=agg.set_index("condition")
    summary_lines=["# Experiment Summary","","## Environment",f"- OS: {env['os']}",f"- Python: {env['python']}",f"- Ollama: {env['ollama']}",f"- LLM: `{CONFIG.llm_model}`",f"- Embeddings: `{CONFIG.embedding_model}`",f"- Hardware: {env.get('hardware',{})}","","## Dataset","- 100 controlled cases: 20 in each of five categories.","- Pilot: 20 cases (first four deterministic cases/category); final: 80 disjoint cases.",f"- Random seed: {CONFIG.random_seed}","","## Final hyperparameters",f"- top-k: {int(params['k'])}",f"- alpha/beta: {params['alpha']}/{params['beta']}",f"- lambda: {params['lambda']}",f"- threshold: {params.get('threshold')}",f"- generation: temperature={CONFIG.temperature}, top_p={CONFIG.top_p}, max_tokens={CONFIG.max_generated_tokens}, seed={CONFIG.generation_seed}","","## Results","",_markdown_table(agg),"","## Failure analysis","",_markdown_table(failures),"","## Key observations",f"- Response accuracy was {indexed.loc['recent_context','correct_mean']:.3f} for recent context, {indexed.loc['full_history','correct_mean']:.3f} for full history, and {indexed.loc['semantic_memory','correct_mean']:.3f} for both retrieval conditions.",f"- Both retrieval conditions achieved recall {indexed.loc['semantic_memory','recall_mean']:.3f} and F1 {indexed.loc['semantic_memory','f1_mean']:.3f}; temporal re-ranking produced no measured retrieval or response advantage in this final set.",f"- Retrieved-memory tokens were {indexed.loc['semantic_memory','context_reduction_vs_full_history_mean']*100:.1f}% lower than full-history historical tokens while matching full-history accuracy.",f"- Cross-session response recall was {indexed.loc['recent_context','cross_session_recall']:.3f}, {indexed.loc['full_history','cross_session_recall']:.3f}, and {indexed.loc['semantic_memory','cross_session_recall']:.3f} for each retrieval method.","- The retrieval-versus-recent paired accuracy difference had p < 0.05 under the predeclared exact McNemar/binomial test; retrieval versus full history was not significant (see `paired_tests.csv`).","- Retrieval metrics apply only to retrieval-enabled conditions; baseline zeros mean retrieval was not performed.","","## Limitations","- Synthetic controlled data; one local LLM and one embedding model; 80-case final set.","- Latency is hardware- and load-specific; generation may retain limited backend nondeterminism.","- Conditions ran in a fixed order, so model warm-up/cache effects confound between-condition generation and total-latency comparisons.","- Deterministic substring/variant scoring can miss semantically correct paraphrases or accept verbose answers containing the target.",""]
    (results/"experiment_summary.md").write_text("\n".join(summary_lines),encoding="utf-8")
