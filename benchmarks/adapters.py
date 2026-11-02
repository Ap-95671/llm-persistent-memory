from dataclasses import dataclass
import hashlib
import json
from pathlib import Path
import re

@dataclass(frozen=True)
class Example:
    id: str
    group: str
    question: str
    history: tuple
    reference: dict

    def model_input(self):
        # Never include answer, evidence, has_answer, or category gold labels here.
        return {"question": self.question, "history": list(self.history)}

def longmemeval(records):
    seen = set()
    for r in records:
        qid = r["question_id"]
        if qid in seen: raise ValueError("duplicate question id")
        seen.add(qid)
        sessions, dates, ids = r["haystack_sessions"],r["haystack_dates"],r["haystack_session_ids"]
        if not len(sessions)==len(dates)==len(ids): raise ValueError("session metadata misalignment")
        history=[]
        for sid,date,turns in zip(ids,dates,sessions):
            for t in turns:
                history.append({"session":sid,"timestamp":date,"role":t["role"],"text":t["content"]})
        yield Example(qid,qid,r["question"],tuple(history),{
            "answer":r["answer"],"question_type":r["question_type"],
            "question_date":r["question_date"],"answer_session_ids":r["answer_session_ids"],
            "abstention":qid.endswith("_abs")})

def locomo(records):
    seen=set()
    for r in records:
        sid=str(r["sample_id"])
        if sid in seen: raise ValueError("duplicate conversation id")
        seen.add(sid); conv=r["conversation"]; history=[]
        keys=sorted((k for k in conv if re.fullmatch(r"session_\d+",k)),key=lambda k:int(k.split('_')[-1]))
        for k in keys:
            for t in conv[k]:
                history.append({"session":k,"timestamp":conv[k+"_date_time"],
                                "speaker":t["speaker"],"text":t["text"],"dialog_id":t["dia_id"]})
        for i,q in enumerate(r["qa"]):
            # Category 5 may provide adversarial_answer without answer.
            yield Example(f"{sid}:{i}",sid,q["question"],tuple(history),{
                "answer":q.get("answer"),"adversarial_answer":q.get("adversarial_answer"),
                "category":q["category"],"evidence":q.get("evidence",[])})

def inspect(path, benchmark):
    content=Path(path).read_bytes(); records=json.loads(content)
    examples=list({"longmemeval":longmemeval,"locomo":locomo}[benchmark](records))
    return {"benchmark":benchmark,"sha256":hashlib.sha256(content).hexdigest(),
            "questions":len(examples),"groups":len({e.group for e in examples}),
            "status":"schema loaded only; no inference or official score"}

if __name__ == "__main__":
    import argparse
    p=argparse.ArgumentParser();p.add_argument("benchmark",choices=["longmemeval","locomo"]);p.add_argument("path")
    a=p.parse_args();print(json.dumps(inspect(a.path,a.benchmark),indent=2))
