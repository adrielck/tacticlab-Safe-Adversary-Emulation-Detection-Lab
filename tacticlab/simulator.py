from __future__ import annotations
import json, uuid, datetime as dt
from pathlib import Path
from typing import Any, Dict, List
import yaml
from .utils import project_root, ensure_dir

def load_scenario(path: Path) -> Dict[str, Any]:
    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)

def simulate_scenario(scenario_path: Path, out_dir: Path | None = None) -> Path:
    root = project_root()
    scenario = load_scenario(scenario_path)
    events: List[Dict[str, Any]] = scenario.get("events", [])
    now = dt.datetime.utcnow()
    base_ts = now
    host_default = scenario.get("host", "host-1")
    user_default = scenario.get("user", "analyst")

    logs_dir = out_dir or (root / "data" / "logs")
    ensure_dir(logs_dir)

    out_file = logs_dir / f"{now.strftime('%Y%m%d_%H%M%S')}_{Path(scenario_path).stem}.jsonl"
    with open(out_file, "w", encoding="utf-8") as f:
        for ev in events:
            ts = base_ts + dt.timedelta(seconds=int(ev.get("time_offset", 0)))
            record = {
                "event_id": str(uuid.uuid4()),
                "timestamp": ts.isoformat() + "Z",
                "host": ev.get("host", host_default),
                "user": ev.get("user", user_default),
                "tactic": ev.get("tactic"),
                "technique_id": ev.get("technique_id"),
                "technique_name": ev.get("technique_name"),
                "command": ev.get("command"),
                "simulated": True,
                "metadata": ev.get("metadata", {}),
                "scenario_id": scenario.get("id"),
                "scenario_name": scenario.get("name"),
                "scenario_desc": scenario.get("description", ""),
            }
            f.write(json.dumps(record) + "\n")
    return out_file
