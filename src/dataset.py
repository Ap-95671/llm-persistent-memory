from __future__ import annotations

import json
from collections import Counter
from datetime import datetime, timedelta, timezone
from pathlib import Path

from config import CONFIG

CATEGORIES = ["stable", "cross_session", "updated", "temporal", "distractor"]

STABLE = [
    ("backend language", "Kotlin", "Which language did I choose for backend work?"),
    ("accessibility testing tool", "Axe", "What tool do I prefer for accessibility checks?"),
    ("database", "PostgreSQL", "Which database did I settle on?"),
    ("editor", "Neovim", "What editor did I say I use?"),
    ("charting library", "Plotly", "Which charting library is my preference?"),
    ("API style", "GraphQL", "What API style do I prefer?"),
    ("unit test framework", "Pytest", "Which unit testing framework did I choose?"),
    ("cloud region", "Mumbai", "Which cloud region did I select?"),
    ("documentation format", "Markdown", "What format do I use for documentation?"),
    ("package manager", "Poetry", "Which Python package manager do I prefer?"),
    ("terminal shell", "Zsh", "What shell do I normally use?"),
    ("CI service", "GitHub Actions", "Which CI service did I choose?"),
    ("license", "Apache 2.0", "What license did I choose for the project?"),
    ("monitoring tool", "Grafana", "Which monitoring tool do I prefer?"),
    ("message broker", "RabbitMQ", "What message broker did I select?"),
    ("CSS approach", "CSS Modules", "Which CSS approach do I prefer?"),
    ("code formatter", "Black", "What code formatter did I select?"),
    ("deployment platform", "Fly.io", "Where did I choose to deploy?"),
    ("search engine", "OpenSearch", "Which search engine did I choose?"),
    ("notebook environment", "JupyterLab", "What notebook environment do I prefer?"),
]

CROSS = [
    ("conference badge name", "A. Prajapati", "What name should appear on my conference badge?"),
    ("frequent flyer number", "SKY-4821", "What frequent-flyer number did I provide?"),
    ("invoice currency", "Singapore dollars", "Which currency should my invoice use?"),
    ("workshop room", "Orchid Hall", "Which room was assigned to my workshop?"),
    ("backup contact", "Mira Sen", "Who is my backup contact?"),
    ("shipping instruction", "Leave with concierge", "What delivery instruction did I give?"),
    ("dietary preference", "Jain vegetarian", "What dietary preference did I record?"),
    ("membership code", "LM-7319", "What is my membership code?"),
    ("preferred timezone", "Asia/Kolkata", "Which timezone should schedules use?"),
    ("locker number", "B-214", "Which locker was allocated to me?"),
    ("support PIN", "583204", "What support PIN did I save?"),
    ("pickup point", "Gate 3", "Where should the driver pick me up?"),
    ("reading group", "Turing Circle", "What is the name of my reading group?"),
    ("lab desk", "D-17", "Which lab desk is mine?"),
    ("printer queue", "north-color", "Which printer queue should I use?"),
    ("repository alias", "memory-lab", "What alias did I assign the repository?"),
    ("hotel booking code", "H7Q2L9", "What was my hotel booking code?"),
    ("emergency phrase", "silver maple", "What emergency phrase did I specify?"),
    ("grant cost centre", "CC-8045", "Which cost centre belongs on the grant expense?"),
    ("seminar track", "Responsible AI", "Which seminar track did I register for?"),
]

UPDATED = [
    ("project meeting", "Monday", "Wednesday", "When is my project meeting?"),
    ("release date", "12 September", "19 September", "What is the current release date?"),
    ("office floor", "fourth floor", "sixth floor", "Which floor is my office on now?"),
    ("reviewer", "Nadia", "Omar", "Who is the current reviewer?"),
    ("demo time", "10:00 AM", "2:30 PM", "What time is the demo now?"),
    ("dataset version", "version 2", "version 3", "Which dataset version should I use?"),
    ("train platform", "platform 5", "platform 8", "Which platform should I go to?"),
    ("budget cap", "$4,000", "$5,500", "What is the revised budget cap?"),
    ("paper title", "Memory at Scale", "Persistent Context", "What is the paper's current title?"),
    ("team lead", "Isha", "Dev", "Who leads the team now?"),
    ("submission venue", "ICML", "NeurIPS", "Where are we submitting now?"),
    ("server port", "8080", "8443", "Which server port should be used now?"),
    ("sprint length", "one week", "two weeks", "What is our current sprint length?"),
    ("report format", "DOCX", "PDF", "Which report format is required now?"),
    ("sample size", "80 participants", "120 participants", "What sample size are we targeting now?"),
    ("branch name", "develop", "research", "Which branch should I work on now?"),
    ("venue", "Room 201", "Auditorium B", "Where will the event take place now?"),
    ("citation style", "APA", "IEEE", "Which citation style should I use now?"),
    ("data retention", "30 days", "90 days", "What is the updated retention period?"),
    ("prototype color", "blue", "charcoal", "What color is the current prototype?"),
]

TEMPORAL = [
    ("current on-call engineer", "Leena", "Ravi", "Who is currently on call?"),
    ("latest experiment run", "run 14", "run 18", "Which is the latest experiment run?"),
    ("active access code", "NOVA-7", "EMBER-4", "What is the active access code?"),
    ("current training phase", "warm-up", "fine-tuning", "Which training phase is active?"),
    ("most recent backup", "Tuesday", "Friday", "When was the most recent backup?"),
    ("current duty station", "Pune", "Bengaluru", "What is my current duty station?"),
    ("latest draft", "draft 3", "draft 6", "Which draft is the latest?"),
    ("active feature flag", "beta-search", "memory-v2", "Which feature flag is active now?"),
    ("current calibration", "profile A", "profile C", "Which calibration profile is current?"),
    ("latest checkpoint", "epoch 4", "epoch 9", "What is the latest checkpoint?"),
    ("current semester", "spring", "autumn", "Which semester is current?"),
    ("active dataset snapshot", "January", "March", "Which dataset snapshot is active?"),
    ("latest survey wave", "wave 1", "wave 3", "Which survey wave is the latest?"),
    ("current lab shift", "morning", "evening", "Which lab shift am I on now?"),
    ("active encryption key", "key K2", "key K5", "Which encryption key is active?"),
    ("current model endpoint", "endpoint east", "endpoint south", "Which model endpoint is current?"),
    ("latest ethics approval", "revision 1", "revision 4", "Which ethics approval revision is latest?"),
    ("current status page", "status-old", "status-live", "Which status page is current?"),
    ("active annotation guide", "guide 2.1", "guide 2.4", "Which annotation guide is active?"),
    ("latest audit file", "audit-April", "audit-July", "Which audit file is the latest?"),
]

DISTRACTOR = [
    ("production database", "PostgreSQL", ["SQLite for mobile tests", "MySQL for the legacy importer", "DuckDB for analysis"], "Which database runs in production?"),
    ("personal laptop color", "midnight blue", ["The office laptop is silver", "The tablet case is navy", "The monitor is black"], "What color is my personal laptop?"),
    ("primary email domain", "research.example", ["Alerts use ops.example", "Students use campus.example", "Archives use old.example"], "What is my primary email domain?"),
    ("main study language", "English", ["Consent forms include Hindi", "A pilot used Marathi", "The UI supports French"], "What is the main study language?"),
    ("production queue", "jobs-critical", ["Tests use jobs-dev", "Batch work uses jobs-bulk", "Old jobs used queue-v1"], "Which queue handles production jobs?"),
    ("preferred coffee", "flat white", ["Guests get espresso", "The lab stocks filter coffee", "Tea is served at meetings"], "What coffee do I prefer?"),
    ("primary phone", "Pixel 9", ["The test phone is an iPhone 13", "The lab phone is a Galaxy S22", "My old phone was a Pixel 6"], "Which phone is my primary one?"),
    ("main project codename", "Juniper", ["The pilot was Cedar", "The dashboard is Birch", "The archive is Pine"], "What is the main project's codename?"),
    ("production cache", "Redis", ["Tests use an in-memory cache", "The prototype used Memcached", "Browsers use local storage"], "Which cache is used in production?"),
    ("doctoral supervisor", "Dr. Rao", ["Dr. Shah reviews statistics", "Dr. Lim leads the lab", "Dr. Bose teaches the seminar"], "Who is my doctoral supervisor?"),
    ("final export folder", "approved-exports", ["Drafts go to draft-exports", "Logs go to export-logs", "Old exports are archived"], "Which folder receives final exports?"),
    ("primary evaluation metric", "macro F1", ["Latency uses milliseconds", "Loss uses cross entropy", "Pilot notes include accuracy"], "What is the primary evaluation metric?"),
    ("main Git remote", "origin", ["The mirror is backup", "Upstream tracks the template", "Archive is read-only"], "Which Git remote is the main one?"),
    ("production API host", "api.prod.example", ["Staging uses api.stage.example", "Docs use docs.example", "Metrics use metrics.example"], "What is the production API host?"),
    ("preferred plotting color", "teal", ["Warnings are orange", "Errors are red", "Baselines are grey"], "Which plotting color do I prefer?"),
    ("main interview room", "Lotus 2", ["Overflow uses Lotus 3", "Briefings use Iris 1", "Storage is beside Lotus 2"], "Which room hosts the main interviews?"),
    ("production model", "Qwen2.5 3B", ["Embeddings use MiniLM", "A baseline used Llama 3", "The draft mentions Qwen 7B"], "Which model is used for production inference?"),
    ("principal investigator", "Prof. Menon", ["Prof. Das owns the dataset", "Dr. Gill manages recruitment", "Prof. Menon also teaches NLP"], "Who is the principal investigator?"),
    ("primary backup region", "Chennai", ["Compute runs in Mumbai", "A replica exists in Delhi", "The team works from Pune"], "Which region is the primary backup location?"),
    ("final paper template", "IEEE conference", ["The proposal used ACM", "Slides use the lab theme", "Notes are plain Markdown"], "Which template is used for the final paper?"),
]


def _mem(case_id: str, n: int, session: int, ts: datetime, text: str, role: str = "user") -> dict:
    return {"id": f"{case_id}-m{n:02d}", "session_id": session, "turn": n, "timestamp": ts.isoformat(), "role": role, "text": text}


def _base(case_id: str, category: str, memories: list[dict], query: str, answer: str, ground: list[str]) -> dict:
    return {"id": case_id, "category": category, "history": memories, "target_historical_memory": ground, "evaluation_query": query, "expected_answer": answer, "acceptable_answers": [answer], "ground_truth_memory_ids": ground}


def generate_cases() -> list[dict]:
    cases, base = [], datetime(2025, 1, 1, 9, tzinfo=timezone.utc)
    fillers = ["I reviewed the project notes.", "We discussed routine scheduling.", "I checked the latest task list."]
    for idx, (subject, value, query) in enumerate(STABLE, 1):
        cid, t = f"stable-{idx:02d}", base + timedelta(days=idx)
        ms = [_mem(cid, 1, 1, t, f"For future reference, my {subject} is {value}."), _mem(cid, 2, 1, t+timedelta(hours=1), fillers[idx%3]), _mem(cid, 3, 1, t+timedelta(hours=2), "I also organized the shared workspace."), _mem(cid, 4, 1, t+timedelta(hours=3), "No other preferences changed today.")]
        cases.append(_base(cid, "stable", ms, query, value, [ms[0]["id"]]))
    for idx, (subject, value, query) in enumerate(CROSS, 1):
        cid, t = f"cross-{idx:02d}", base + timedelta(days=40+idx)
        ms = [_mem(cid, 1, 1, t, f"Please remember that my {subject} is {value}."), _mem(cid, 2, 1, t+timedelta(hours=1), "That concludes this session."), _mem(cid, 3, 2, t+timedelta(days=7), "I started a new session to plan next week's work."), _mem(cid, 4, 2, t+timedelta(days=7, minutes=5), "We can keep today's discussion brief.")]
        cases.append(_base(cid, "cross_session", ms, query, value, [ms[0]["id"]]))
    for idx, (subject, old, new, query) in enumerate(UPDATED, 1):
        cid, t = f"updated-{idx:02d}", base + timedelta(days=80+idx)
        ms = [_mem(cid, 1, 1, t, f"The {subject} is {old}."), _mem(cid, 2, 1, t+timedelta(hours=2), "I noted that initial plan."), _mem(cid, 3, 2, t+timedelta(days=5), f"Update: the {subject} has changed to {new}; use this instead."), _mem(cid, 4, 2, t+timedelta(days=5, hours=1), "I then reviewed unrelated action items."), _mem(cid, 5, 2, t+timedelta(days=5, hours=2), "The rest of the plan is unchanged.")]
        c = _base(cid, "updated", ms, query, new, [ms[2]["id"]]); c["superseded_memory_ids"] = [ms[0]["id"]]; cases.append(c)
    for idx, (subject, old, new, query) in enumerate(TEMPORAL, 1):
        cid, t = f"temporal-{idx:02d}", base + timedelta(days=120+idx)
        ms = [_mem(cid, 1, 1, t, f"As of this morning, the {subject} is {old}."), _mem(cid, 2, 1, t+timedelta(days=2), f"At the latest check, the {subject} became {new}."), _mem(cid, 3, 1, t+timedelta(days=2, hours=1), "The chronological log is authoritative."), _mem(cid, 4, 1, t+timedelta(days=2, hours=2), "I filed the remaining notes.")]
        c = _base(cid, "temporal", ms, query, new, [ms[1]["id"]]); c["superseded_memory_ids"] = [ms[0]["id"]]; cases.append(c)
    for idx, (subject, value, distractors, query) in enumerate(DISTRACTOR, 1):
        cid, t = f"distractor-{idx:02d}", base + timedelta(days=160+idx)
        ms = [_mem(cid, 1, 1, t, f"The {subject} is {value}."), *[_mem(cid, j+2, 1, t+timedelta(hours=j+1), x) for j,x in enumerate(distractors)], _mem(cid, 5, 1, t+timedelta(hours=5), "I finished cataloguing these related details."), _mem(cid, 6, 1, t+timedelta(hours=6), "Nothing else needs attention.")]
        c = _base(cid, "distractor", ms, query, value, [ms[0]["id"]]); c["distractor_memory_ids"] = [m["id"] for m in ms[1:4]]; cases.append(c)
    return cases


def validate_cases(cases: list[dict], expected_total: int | None = None) -> dict:
    errors, ids = [], []
    if expected_total is not None and len(cases) != expected_total: errors.append(f"expected {expected_total} cases, found {len(cases)}")
    counts = Counter(c["category"] for c in cases)
    if expected_total == 100:
        for cat in CATEGORIES:
            if counts[cat] != 20: errors.append(f"{cat}: expected 20, found {counts[cat]}")
    for case in cases:
        if not case.get("evaluation_query", "").strip(): errors.append(f"{case.get('id')}: empty query")
        if not case.get("expected_answer", "").strip(): errors.append(f"{case.get('id')}: empty expected answer")
        mids = [m["id"] for m in case.get("history", [])]; ids.extend(mids)
        missing = set(case.get("ground_truth_memory_ids", [])) - set(mids)
        if missing: errors.append(f"{case['id']}: missing ground truth {sorted(missing)}")
        try:
            times = [datetime.fromisoformat(m["timestamp"]) for m in case["history"]]
            if times != sorted(times): errors.append(f"{case['id']}: timestamps not ordered")
        except Exception as exc: errors.append(f"{case['id']}: invalid timestamp: {exc}")
        if case["category"] in {"updated", "temporal"}:
            superseded = set(case.get("superseded_memory_ids", []))
            if not superseded or superseded & set(case["ground_truth_memory_ids"]): errors.append(f"{case['id']}: invalid update pair")
    duplicates = [mid for mid, n in Counter(ids).items() if n > 1]
    if duplicates: errors.append(f"duplicate memory IDs: {duplicates[:5]}")
    if errors: raise ValueError("Dataset validation failed:\n" + "\n".join(errors))
    return {"case_count": len(cases), "category_counts": dict(counts), "memory_count": len(ids)}


def generate_and_save(data_dir: Path) -> dict:
    cases = generate_cases(); report = validate_cases(cases, 100)
    pilot_ids = {f"{prefix}-{n:02d}" for prefix in ["stable", "cross", "updated", "temporal", "distractor"] for n in range(1, 5)}
    pilot, final = [c for c in cases if c["id"] in pilot_ids], [c for c in cases if c["id"] not in pilot_ids]
    validate_cases(pilot, 20); validate_cases(final, 80)
    data_dir.mkdir(parents=True, exist_ok=True)
    payload = {"random_seed": CONFIG.random_seed, "cases": cases}
    (data_dir/"test_cases.json").write_text(json.dumps(payload, indent=2)+"\n")
    (data_dir/"pilot_cases.json").write_text(json.dumps({"selection":"first four deterministic cases from each category before any evaluation", "random_seed":CONFIG.random_seed, "cases":pilot}, indent=2)+"\n")
    (data_dir/"final_cases.json").write_text(json.dumps({"excludes_pilot":True, "random_seed":CONFIG.random_seed, "cases":final}, indent=2)+"\n")
    return report | {"pilot_count":len(pilot), "final_count":len(final)}


if __name__ == "__main__":
    print(generate_and_save(Path(__file__).resolve().parents[1]/"data"))
