from dataclasses import replace
from datetime import datetime,timedelta,timezone
import pytest
from pmemory.policy import Candidate,RetentionPolicy
from pmemory.store import MemoryStore
from pmemory.baselines import NoMemory,Mem0Baseline

NOW=datetime(2026,1,1,tzinfo=timezone.utc)
def candidate(**kw):
    return replace(Candidate("alice","theme","prefers dark theme","personalization",NOW,NOW+timedelta(days=10),True,False),**kw)

@pytest.fixture
def store(tmp_path):
    s=MemoryStore(tmp_path/"memory.db");yield s;s.close()

@pytest.mark.parametrize("change",[{"consent":False},{"sensitive":True},{"purpose":"ads"},{"expires_at":NOW},{"expires_at":NOW+timedelta(days=31)},{"observed_at":NOW+timedelta(days=1)}])
def test_deny_does_not_write(store,change):
    assert store.adjudicate(candidate(**change),now=NOW).action=="reject"
    assert not store.retrieve("alice","theme","personalization",now=NOW)

def test_updates_stale_conflicts_and_tenant_isolation(store):
    c=candidate();assert store.adjudicate(c,now=NOW).action=="retain"
    assert store.adjudicate(c,now=NOW).action=="reject"
    later=NOW+timedelta(hours=1)
    assert store.adjudicate(candidate(text="prefers light theme",observed_at=later),now=later).action=="update"
    assert store.adjudicate(c,now=later).action=="reject"
    assert not store.retrieve("bob","theme","personalization",now=later)
    assert store.retrieve("alice","theme","personalization",now=later)[0].text=="prefers light theme"

def test_persistence_expiry_forget_and_changed_policy(tmp_path):
    p=tmp_path/"memory.db";s=MemoryStore(p);s.adjudicate(candidate(),now=NOW);s.close()
    s=MemoryStore(p);assert s.retrieve("alice","theme","personalization",now=NOW)
    assert not s.retrieve("alice","theme","personalization",now=NOW+timedelta(days=11))
    s.policy=RetentionPolicy(purposes=());assert not s.retrieve("alice","theme","personalization",now=NOW)
    s.forget("alice","theme");assert s.db.execute("SELECT COUNT(*) FROM memory").fetchone()[0]==0;s.close()

def test_naive_time_rejected(store):
    with pytest.raises(ValueError):store.adjudicate(candidate(observed_at=datetime(2026,1,1)),now=NOW)

def test_no_memory_zero_and_last_two():
    assert NoMemory(0).history([1,2,3])==[]
    assert NoMemory().history([1,2,3])==[2,3]

def test_mem0_preserves_inference_and_scope():
    class Fake:
        def add(self,*a,**k):return k
        def search(self,*a,**k):return k
    b=Mem0Baseline(Fake());assert b.ingest([],"alice")=={"user_id":"alice","infer":True}
    assert b.retrieve("theme","alice",3)=={"user_id":"alice","limit":3}
