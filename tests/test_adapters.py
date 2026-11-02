import json
import pytest
from benchmarks.adapters import longmemeval,locomo

def test_longmemeval_labels_never_enter_inputs():
    r={"question_id":"q_abs","question":"query","answer":"GOLD_SECRET","question_type":"multi-session","question_date":"date","haystack_session_ids":["s"],"haystack_dates":["date"],"haystack_sessions":[[{"role":"user","content":"fact","has_answer":True}]],"answer_session_ids":["s"]}
    e=list(longmemeval([r]))[0];p=json.dumps(e.model_input())
    assert "GOLD_SECRET" not in p and "has_answer" not in p and "answer_session_ids" not in p
    assert e.reference["abstention"]
    with pytest.raises(ValueError):list(longmemeval([r,r]))

def test_locomo_numeric_order_and_adversarial_missing_answer():
    def turn(n):return {"speaker":"A","text":str(n),"dia_id":str(n)}
    r={"sample_id":"x","conversation":{"session_10":[turn(10)],"session_10_date_time":"later","session_2":[turn(2)],"session_2_date_time":"earlier"},"qa":[{"question":"query","category":5,"adversarial_answer":"TRAP"}]}
    e=list(locomo([r]))[0]
    assert [t["text"] for t in e.history]==["2","10"]
    assert "TRAP" not in json.dumps(e.model_input())
    assert e.reference["answer"] is None
