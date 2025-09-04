from __future__ import annotations
import json, datetime as dt
from pathlib import Path
from typing import Dict, Any, List, Set
from .utils import project_root, ensure_dir

def load_jsonl(path: Path) -> List[Dict[str, Any]]:
    if not path.exists(): return []
    rows = []
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            if line.strip():
                rows.append(json.loads(line))
    return rows

def build_report() -> Path:
    base = project_root()
    logs_dir = base / "data" / "logs"
    det_file = base / "data" / "detections" / "detections.jsonl"
    reports_dir = base / "reports"
    ensure_dir(reports_dir)

    log_files = sorted(logs_dir.glob("*.jsonl"))
    detections = load_jsonl(det_file)

    techniques_seen: Set[str] = set()
    scenarios: Set[str] = set()
    alerts_per_rule: Dict[str, int] = {}

    for p in log_files:
        for ev in load_jsonl(p):
            if ev.get("technique_id"):
                techniques_seen.add(f"{ev['technique_id']} - {ev.get('technique_name','')}")
            if ev.get("scenario_name"):
                scenarios.add(ev["scenario_name"])

    for d in detections:
        key = f\"{d.get('rule_id')} | {d.get('rule_title')}\"
        alerts_per_rule[key] = alerts_per_rule.get(key, 0) + 1

    now = dt.datetime.now().strftime(\"%Y%m%d_%H%M\")
    out = reports_dir / f\"{now}_report.md\"
    with open(out, \"w\", encoding=\"utf-8\") as f:
        f.write(f\"# tacticlab — Relatório de Execução ({now})\\n\\n\")
        f.write(\"## Cenários executados\\n\")
        for s in sorted(scenarios):
            f.write(f\"- {s}\\n\")
        if not scenarios:
            f.write(\"- (nenhum)\\n\")
        f.write(\"\\n## Técnicas vistas (MITRE ATT&CK)\\n\")
        for t in sorted(techniques_seen):
            f.write(f\"- {t}\\n\")
        if not techniques_seen:
            f.write(\"- (nenhuma)\\n\")
        f.write(\"\\n## Alertas por regra\\n\")
        if alerts_per_rule:
            for k, v in sorted(alerts_per_rule.items(), key=lambda x: -x[1]):
                f.write(f\"- **{k}**: {v} alertas\\n\")
        else:
            f.write(\"- (nenhum)\\n\")
        f.write(\"\\n> Observação: os dados acima são sintéticos, produzidos pelo simulador seguro.\\n\")
    return out
