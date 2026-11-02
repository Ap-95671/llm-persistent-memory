from __future__ import annotations

import argparse
import os
from datetime import datetime, timezone
from pathlib import Path

_PROJECT = Path(__file__).resolve().parent
os.environ.setdefault("MPLCONFIGDIR", str(_PROJECT/".cache/matplotlib"))
os.environ.setdefault("XDG_CACHE_HOME", str(_PROJECT/".cache"))

from config import CONFIG
from experiments.final_evaluation import run_final
from experiments.pilot import run_pilot
from src.context_builder import TokenCounter
from src.dataset import generate_and_save, validate_cases
from src.embeddings import EmbeddingModel
from src.llm import OllamaLLM
from src.utils import read_json, set_seeds


def main()->None:
    parser=argparse.ArgumentParser(); parser.add_argument("phase",choices=["dataset","pilot","final","all"],nargs="?",default="all"); args=parser.parse_args()
    project=Path(__file__).resolve().parent; set_seeds(CONFIG.random_seed)
    if args.phase in {"dataset","all"}: print("Dataset:",generate_and_save(project/"data"),flush=True)
    if args.phase=="dataset": return
    validate_cases(read_json(project/"data/pilot_cases.json")["cases"],20); validate_cases(read_json(project/"data/final_cases.json")["cases"],80)
    embedder=EmbeddingModel(CONFIG.embedding_model)
    if args.phase in {"pilot","all"}: _,params=run_pilot(project,embedder); print("Frozen pilot parameters:",params,flush=True)
    else: params=read_json(project/"results/frozen_parameters.json")
    if args.phase=="pilot": return
    from src.reporting import write_outputs
    counter=TokenCounter(CONFIG.tokenizer_model)
    llm=OllamaLLM(CONFIG.ollama_url,CONFIG.llm_model,CONFIG.system_prompt,{"temperature":CONFIG.temperature,"top_p":CONFIG.top_p,"num_predict":CONFIG.max_generated_tokens,"seed":CONFIG.generation_seed,"num_ctx":CONFIG.context_window})
    models=[m.get("name") for m in llm.check().get("models",[])];
    if not any(name and name.startswith(CONFIG.llm_model) for name in models): raise RuntimeError(f"Required Ollama model {CONFIG.llm_model} unavailable; installed={models}")
    df=run_final(project,embedder,counter,llm,params)
    stamp=datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ"); write_outputs(project,df,params,project/"runs"/stamp)
    print(f"Completed {len(df)} evaluations in run {stamp}",flush=True)


if __name__=="__main__": main()
