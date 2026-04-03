from datetime import datetime, timezone
from typing import Dict
import uuid


def now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def make_id(prefix: str) -> str:
    return f"{prefix}_{uuid.uuid4().hex[:8]}"


users: Dict[str, dict] = dict()
users_by_email: Dict[str, str] = dict()

documents: Dict[str, dict] = dict()
permissions: Dict[str, Dict[str, str]] = dict()
sessions: Dict[str, dict] = dict()
ai_jobs: Dict[str, dict] = dict()