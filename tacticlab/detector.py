from __future__ import annotations
import json, re
from pathlib import Path
from typing import Any, Dict, Iterable, List
import yaml
from .utils import project_root, ensure_dir

def iter_log_events(logs_dir: Path | None) -> Iterable[Dict[str, Any]]:
    base = logs_dir or (project_root() / "data" / "logs")
    for p in sorted(base.glob("*.jsonl")):
        with open(p, "r", encoding="utf-8") as f:
            for line in f:
                if line.strip():
                    yield json.loads(line)

def load_rules(rules_path: Path | None) -> List[Dict[str, Any]]:
    rules: List[Dict[str, Any]] = []
    base = rules_path or (project_root() / "rules")
    for p in sorted(base.glob("*.yaml")):
        with open(p, "r", encoding="utf-8") as f:
            rules.append(yaml.safe_load(f))
    return rules

def event_matches_rule(event: Dict[str, Any], rule: Dict[str, Any]) -> bool:
    m = rule.get("match", {})
    def as_list(x):
        if not x: return []
        return x if isinstance(x, list) else [x]
    # equals/contains/regex -> any-of semantics
    for key in ("equals", "contains", "regex"):
        items = as_list(m.get(key))
        if not items: 
            continue
        matched = False
        for it in items:
            field = it.get("field")
            value = str(it.get("value", ""))
            ev_val = str(event.get(field, ""))
            if key == "equals" and ev_val == value:
                matched = True
            elif key == "contains" and value.lower() in ev_val.lower():
                matched = True
            elif key == "regex" and re.search(value, ev_val):
                matched = True
        if matched:
            return True
    return False

def run_detection(rules_path: Path | None = None, logs_dir: Path | None = None, out_dir: Path | None = None) -> Path:
    base = project_root()
    rules = load_rules(rules_path)
    detections_dir = out_dir or (base / "data" / "detections")
    ensure_dir(detections_dir)
    out_file = detections_dir / "detections.jsonl"
    with open(out_file, "w", encoding="utf-8") as out:
        for ev in iter_log_events(logs_dir):
            for rule in rules:
                if event_matches_rule(ev, rule):
                    det = {
                        "rule_id": rule.get("id"),
                        "rule_title": rule.get("title"),
                        "severity": rule.get("severity", "low"),
                        "tactic": rule.get("tactic"),
                        "technique_id": rule.get("technique_id"),
                        "technique_name": rule.get("technique_name"),
                        "event_id": ev.get("event_id"),
                        "timestamp": ev.get("timestamp"),
                        "host": ev.get("host"),
                        "user": ev.get("user"),
                        "matched_fields": rule.get("match"),
                        "scenario_id": ev.get("scenario_id"),
                        "scenario_name": ev.get("scenario_name"),
                    }
                    out.write(json.dumps(det) + "\n")
    return out_file
