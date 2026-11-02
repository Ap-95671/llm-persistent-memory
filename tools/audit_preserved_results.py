"""Recompute historical summary and paired uncertainty without model/API calls."""
import collections
import hashlib
import json
import math
from pathlib import Path
import random
import statistics

ROOT=Path(__file__).resolve().parents[1]

def wilson(k,n):
    z=1.959963984540054;p=k/n;d=1+z*z/n
    center=(p+z*z/(2*n))/d
    half=z*math.sqrt(p*(1-p)/n+z*z/(4*n*n))/d
    return [center-half,center+half]

def main():
    raw=ROOT/'results/raw_results.json';data=json.loads(raw.read_bytes())
    cases=json.loads((ROOT/'data/final_cases.json').read_text())["cases"]
    refs={c['id']:c for c in cases};conditions=collections.defaultdict(dict)
    for row in data:
        cid=row['case_id'];cond=row['condition']
        assert cid in refs and cid not in conditions[cond], "invalid or duplicate pair"
        assert row['expected_answer']==refs[cid]['expected_answer']
        # The historical answer scorer is deliberately preserved, including its limits.
        import re
        def normalize(s):return re.sub(r"[^a-z0-9\s]", "",s.lower()).strip()
        # Check historical stored score using its actual source implementation.
        import sys
        sys.path.insert(0,str(ROOT))
        from src.utils import normalize_text
        actual=normalize_text(row['generated_answer'])
        expected=normalize_text(row['expected_answer'])
        variants=[normalize_text(v) for v in refs[cid].get('acceptable_answers',[])]
        correct=bool(actual) and any(actual==v or (v and v in actual) for v in [expected,*variants])
        assert bool(row['correct'])==correct, "historical scoring mismatch"
        conditions[cond][cid]=row
    assert len(data)==320 and len(conditions)==4
    assert all(set(rows)==set(refs) for rows in conditions.values())
    summary={}
    for name,rows in sorted(conditions.items()):
        rows=list(rows.values());n=len(rows);k=sum(bool(r['correct']) for r in rows)
        summary[name]={"n":n,"correct":k,"accuracy":k/n,"accuracy_wilson95":wilson(k,n),"input_tokens_mean":statistics.mean(r['input_tokens'] for r in rows)}
    # Resample paired case differences within the five synthetic categories.
    # These are conditional resampling intervals, not population generalization evidence.
    strata=collections.defaultdict(list)
    for cid,c in refs.items():strata[c['category']].append(cid)
    comparisons=[]
    for left,right in [('semantic_memory','full_history'),('semantic_temporal_memory','semantic_memory')]:
        rng=random.Random(20261102);diff={cid:int(conditions[left][cid]['correct'])-int(conditions[right][cid]['correct']) for cid in refs}
        samples=sorted(sum(diff[rng.choice(ids)] for ids in strata.values() for _ in ids)/len(refs) for _ in range(10000))
        comparisons.append({"a":left,"b":right,"paired_accuracy_difference":statistics.mean(diff.values()),"stratified_paired_bootstrap95":[samples[249],samples[9749]],"resamples":10000,"seed":20261102})
    report={"kind":"reanalysis of preserved outputs; inference not rerun","source_sha256":hashlib.sha256(raw.read_bytes()).hexdigest(),"summary":summary,"comparisons":comparisons,"limitations":["Synthetic templates, not a random population sample; intervals describe conditional case variability.","No privacy-policy, Mem0, LongMemEval or LoCoMo score is present.","Fixed condition order confounds latency; recorded total excludes precomputed embeddings and indexing.","Recent-context targets were deliberately outside its window; zero accuracy is a dataset design consequence."]}
    (ROOT/'results/reanalysis.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps(report,indent=2))

if __name__=='__main__':main()
