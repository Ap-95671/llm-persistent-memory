from datetime import datetime, timedelta, timezone

import numpy as np

from src.dataset import CATEGORIES, generate_cases, validate_cases
from src.evaluation import answer_correct, retrieval_metrics
from src.memory_store import MemoryStore
from src.retrieval import semantic_retrieve, temporal_retrieve


def test_dataset_shape_and_validity():
    cases=generate_cases(); report=validate_cases(cases,100)
    assert report["case_count"]==100
    assert report["category_counts"]=={category:20 for category in CATEGORIES}


def test_retrieval_metrics_empty_safe():
    assert retrieval_metrics([], ["m1"])=={"precision":0.0,"recall":0.0,"f1":0.0,"recall_at_k":0.0}
    assert retrieval_metrics([], [])["f1"]==1.0


def test_answer_scoring_normalizes_punctuation():
    assert answer_correct("The answer is PostgreSQL.","PostgreSQL",["Postgres"])
    assert not answer_correct("MySQL","PostgreSQL",[])


def test_semantic_and_temporal_retrieval():
    now=datetime(2025,1,10,tzinfo=timezone.utc)
    memories=[{"id":"old","text":"old","timestamp":(now-timedelta(days=8)).isoformat()},{"id":"new","text":"new","timestamp":(now-timedelta(hours=1)).isoformat()}]
    vectors=np.array([[1.0,0.0],[0.9,np.sqrt(1-.9**2)]],dtype="float32")
    store=MemoryStore(memories,vectors); query=np.array([1.0,0.0],dtype="float32")
    semantic,_=semantic_retrieve(store,query,1); temporal,_=temporal_retrieve(store,query,1,.5,.5,.2,now)
    assert semantic[0]["id"]=="old"
    assert temporal[0]["id"]=="new"

