from __future__ import annotations
import click
from pathlib import Path
from rich.console import Console
from .simulator import simulate_scenario
from .detector import run_detection
from .reporter import build_report
from .utils import project_root

console = Console()

@click.group()
def cli():
    \"\"\"CLI principal do tacticlab.\"\"\"
    pass

@cli.command()
@click.option("--scenario", "-s", type=str, required=True, help="Caminho para o arquivo YAML do cenário.")
@click.option("--out", "-o", type=str, default=None, help="Diretório de saída para os logs.")
def simulate(scenario: str, out: str | None):
    \"\"\"Gera logs sintéticos para um cenário ATT&CK.\"\"\"
    p = Path(scenario)
    if not p.exists():
        rp = project_root() / scenario
        if rp.exists():
            p = rp
        else:
            console.print(f"[red]Cenário não encontrado:[/red] {scenario}")
            raise SystemExit(1)
    out_dir = Path(out) if out else None
    log_path = simulate_scenario(p, out_dir)
    console.print(f"[green]OK[/green] Logs gerados em: {log_path}")

@cli.command()
@click.option("--rules", "-r", type=str, default=None, help="Diretório/arquivo de regras YAML.")
@click.option("--logs", "-l", type=str, default=None, help="Diretório com logs JSONL.")
def detect(rules: str | None, logs: str | None):
    \"\"\"Roda engine simples de detecção sobre os logs sintéticos.\"\"\"
    rules_path = Path(rules) if rules else None
    logs_dir = Path(logs) if logs else None
    out = run_detection(rules_path, logs_dir)
    console.print(f"[green]OK[/green] Detecções escritas em: {out}")

@cli.command()
def report():
    \"\"\"Gera um relatório Markdown com cenários, técnicas vistas e alertas por regra.\"\"\"
    out = build_report()
    console.print(f"[green]OK[/green] Relatório: {out}")

if __name__ == "__main__":
    cli()
