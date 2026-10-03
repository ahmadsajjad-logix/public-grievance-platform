"""Versioned, bundled local-source references; no runtime network access."""
import json
from functools import lru_cache
from pathlib import Path


@lru_cache(maxsize=1)
def library():
    path = Path(__file__).resolve().parents[1] / "data" / "department_documents.json"
    if not path.exists():
        return {"documents": [], "chunks": []}
    return json.loads(path.read_text(encoding="utf-8"))


def scoped_references(department_ids, region):
    return [d for d in library()["chunks"]
            if set(d["department_ids"]) & set(department_ids)
            and (not d["region"] or region in d["region"])]
