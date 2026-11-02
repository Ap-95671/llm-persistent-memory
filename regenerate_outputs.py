"""Regenerate derived reports from preserved raw JSON without invoking an LLM."""
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd

from src.evaluation import classify_failure
from src.reporting import write_outputs
from src.utils import read_json


project=Path(__file__).resolve().parent
df=pd.DataFrame(read_json(project/"results/raw_results.json"))
case_map={case["id"]:case for case in read_json(project/"data/final_cases.json")["cases"]}
df["failure_type"]=[classify_failure(row,case_map[row["case_id"]]) for row in df.to_dict(orient="records")]
params=read_json(project/"results/frozen_parameters.json")
stamp=datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ-report-recovery")
write_outputs(project,df,params,project/"runs"/stamp)
print(f"Regenerated derived outputs from {len(df)} preserved raw records into {stamp}")
