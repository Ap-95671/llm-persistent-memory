from dataclasses import dataclass
from datetime import datetime
from typing import Literal

@dataclass(frozen=True)
class Candidate:
    owner: str
    key: str
    text: str
    purpose: str
    observed_at: datetime
    expires_at: datetime
    consent: bool = False
    sensitive: bool = True

@dataclass(frozen=True)
class Decision:
    action: Literal["retain", "update", "reject", "forget"]
    reason: str

class RetentionPolicy:
    """Explicit trusted labels are required; arbitrary conversation cannot set consent."""
    def __init__(self, purposes=("personalization",), max_retention_days=30):
        self.purposes = frozenset(purposes)
        self.max_retention_days = max_retention_days

    def check(self, c: Candidate, now: datetime) -> str | None:
        for dt in (now, c.observed_at, c.expires_at):
            if dt.tzinfo is None or dt.utcoffset() is None:
                raise ValueError("timezone-aware timestamps required")
        if not all(x.strip() for x in (c.owner, c.key, c.text, c.purpose)):
            return "missing required field"
        if not c.consent: return "no explicit retention consent"
        if c.sensitive: return "sensitive candidate"
        if c.purpose not in self.purposes: return "purpose not allowed"
        if c.observed_at > now: return "future observation"
        if c.expires_at <= now: return "expired"
        if (c.expires_at - c.observed_at).total_seconds() > self.max_retention_days * 86400:
            return "retention exceeds policy"
        return None
