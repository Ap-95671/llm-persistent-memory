import json
import sqlite3
from dataclasses import asdict
from datetime import datetime
from .policy import Candidate, Decision, RetentionPolicy

class MemoryStore:
    """SQLite prototype. Owner IDs must come from a trusted authenticated caller."""
    def __init__(self, path, policy=None):
        self.db = sqlite3.connect(path)
        self.policy = policy or RetentionPolicy()
        self.db.execute("CREATE TABLE IF NOT EXISTS memory (owner TEXT, key TEXT, payload TEXT, PRIMARY KEY(owner,key))")
        self.db.commit()

    def close(self): self.db.close()

    @staticmethod
    def decode(payload):
        d = json.loads(payload)
        for k in ("observed_at", "expires_at"): d[k] = datetime.fromisoformat(d[k])
        return Candidate(**d)

    def adjudicate(self, c: Candidate, *, now: datetime) -> Decision:
        reason = self.policy.check(c, now)
        if reason: return Decision("reject", reason)
        with self.db:
            row = self.db.execute("SELECT payload FROM memory WHERE owner=? AND key=?", (c.owner,c.key)).fetchone()
            if row and self.decode(row[0]).observed_at >= c.observed_at:
                return Decision("reject", "duplicate or stale observation")
            payload = asdict(c)
            for k in ("observed_at", "expires_at"): payload[k] = payload[k].isoformat()
            self.db.execute("INSERT OR REPLACE INTO memory VALUES(?,?,?)", (c.owner,c.key,json.dumps(payload)))
        return Decision("update" if row else "retain", "eligible explicit candidate")

    def retrieve(self, owner: str, query: str, purpose: str, *, now: datetime, limit=5):
        if limit < 0: raise ValueError("limit must be nonnegative")
        # Policy is reapplied on read: expiry and changed policy cannot be bypassed.
        rows = self.db.execute("SELECT payload FROM memory WHERE owner=?", (owner,)).fetchall()
        eligible = [self.decode(r[0]) for r in rows]
        eligible = [c for c in eligible if c.purpose == purpose and self.policy.check(c,now) is None]
        terms = set(query.casefold().split())
        eligible.sort(key=lambda c: (-len(terms & set(c.text.casefold().split())), c.key))
        return eligible[:limit]

    def purge_expired(self, *, now: datetime):
        # Functional deletion only: SQLite journals/backups may retain bytes.
        with self.db:
            rows = self.db.execute("SELECT owner,key,payload FROM memory").fetchall()
            for owner,key,payload in rows:
                if self.decode(payload).expires_at <= now:
                    self.db.execute("DELETE FROM memory WHERE owner=? AND key=?",(owner,key))

    def forget(self, owner: str, key: str) -> Decision:
        with self.db: self.db.execute("DELETE FROM memory WHERE owner=? AND key=?",(owner,key))
        return Decision("forget", "logical deletion; no secure-erasure guarantee")
