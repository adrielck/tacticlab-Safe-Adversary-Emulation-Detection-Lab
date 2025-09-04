# tacticlab — Safe Adversary Emulation & Detection Lab

![Python](https://img.shields.io/badge/Python-3.10%2B-blue)
![License: MIT](https://img.shields.io/badge/License-MIT-green)
![Safe-By-Design](https://img.shields.io/badge/Safe--By--Design-Yes-brightgreen)

**tacticlab** é um laboratório **seguro por design** para demonstrar habilidades de **Red Team** e **Detection Engineering** sem executar código malicioso.
Ele **simula TTPs do MITRE ATT&CK** e escreve **logs sintéticos** em JSONL; em seguida, uma engine simples aplica **regras de detecção** (YAML) e gera **achados** + **relatório** em Markdown.

> ⚠️ **Segurança/Ética**: Nada é executado no sistema. “Comandos” aparecem apenas como strings em logs sintéticos para fins didáticos.

---

## Sumário
- [Arquitetura](#arquitetura)
- [Destaques](#destaques)
- [Stack e Requisitos](#stack-e-requisitos)
- [Estrutura do Repositório](#estrutura-do-repositório)
- [Instalação](#instalação)
- [Uso Rápido (CLI)](#uso-rápido-cli)
- [Formato de Cenários (YAML)](#formato-de-cenários-yaml)
- [Formato de Regras (YAML)](#formato-de-regras-yaml)
- [Esquemas de Dados (JSONL)](#esquemas-de-dados-jsonl)
- [Relatórios](#relatórios)
- [Fluxo de Trabalho Típico](#fluxo-de-trabalho-típico)
- [Extensões e Roadmap](#extensões-e-roadmap)
- [Boas Práticas / Limitações](#boas-práticas--limitações)
- [Contribuição](#contribuição)
- [Autor](#autor)
- [Licença](#licença)

---

## Arquitetura

Módulos principais:

- `tacticlab/simulator.py`  
  Lê um **cenário** (YAML) e gera **eventos sintéticos** (JSONL) mapeados a táticas/técnicas do **MITRE ATT&CK**.

- `tacticlab/detector.py`  
  Lê **regras** (YAML) e **logs** (JSONL). Para cada evento, avalia as condições e escreve **detecções** (JSONL) quando houver match.

- `tacticlab/reporter.py`  
  Consolida a execução: lista cenários, técnicas vistas e contagem de alertas por regra em um **relatório Markdown**.

- `tacticlab/cli.py`  
  Interface de linha de comando (via **Click**): `simulate`, `detect`, `report`.

Fluxo lógico:

```
Cenário (YAML) ──> simulator ──> logs JSONL ──┐
                                             ├─> detector (regras YAML) ──> detecções JSONL ──> reporter ──> relatório .md
Regras (YAML) ───────────────────────────────┘
```

---

## Destaques
- **Seguro por design**: não executa processos nem altera o SO; apenas gera **texto** em arquivos.
- **MITRE ATT&CK mapeado**: cada evento inclui `tactic`, `technique_id`, `technique_name`.
- **Detecção em YAML**: regras “estilo Sigma” simplificadas (`equals`, `contains`, `regex`).
- **Relatório automático**: cenários rodados, técnicas vistas e alertas por regra.

---

## Stack e Requisitos
- **Python** 3.10+
- Bibliotecas:
  - `click` (CLI)
  - `rich` (saída legível no terminal)
  - `PyYAML` (parsing YAML)

Instalação:
```bash
pip install -r requirements.txt
```

---

## Estrutura do Repositório

```
tacticlab/
├─ tacticlab/
│  ├─ __init__.py
│  ├─ cli.py              # CLI (simulate/detect/report)
│  ├─ simulator.py        # Gerador de logs sintéticos
│  ├─ detector.py         # Engine simples de detecção
│  ├─ reporter.py         # Geração de relatório Markdown
│  └─ utils.py
├─ scenarios/             # Cenários MITRE ATT&CK (simulados)
│  ├─ initial_access_phishing.yaml
│  ├─ credential_dumping_sim.yaml
│  ├─ lateral_movement_sim.yaml
│  └─ exfiltration_sim.yaml
├─ rules/                 # Regras exemplo (YAML)
│  ├─ credential_access_sim.yaml
│  ├─ persistence_runkeys_sim.yaml
│  └─ discovery_powershell_enum_sim.yaml
├─ data/
│  ├─ logs/               # Saída: eventos (.jsonl)
│  └─ detections/         # Saída: detecções (.jsonl)
├─ reports/               # Saída: relatórios (.md)
├─ requirements.txt
├─ LICENSE
└─ README.md
```

---

## Instalação

```bash
python -m venv .venv
# Linux/macOS:
source .venv/bin/activate
# Windows (PowerShell):
# .venv\Scripts\Activate.ps1

pip install -r requirements.txt
```

---

## Uso Rápido (CLI)

**Simular um cenário** (gera logs em `data/logs`):
```bash
python -m tacticlab.cli simulate -s scenarios/credential_dumping_sim.yaml
```

**Rodar detecções** (varre logs e aplica regras):
```bash
python -m tacticlab.cli detect -r rules/ -l data/logs
```

**Gerar relatório** (escreve `.md` em `reports/`):
```bash
python -m tacticlab.cli report
```

Ajuda:
```bash
python -m tacticlab.cli --help
python -m tacticlab.cli simulate --help
python -m tacticlab.cli detect --help
python -m tacticlab.cli report --help
```

---

## Formato de Cenários (YAML)

Um **cenário** descreve uma cadeia de eventos com mapeamento para ATT&CK:

```yaml
id: SC-CREDS-001
name: Credential Access — OS Credential Dumping (Simulated)
description: Cadeia de eventos representando coleta de credenciais, apenas simulada.
host: host-2
user: user2
events:
  - time_offset: 0                     # segundos a partir do início
    tactic: discovery                  # tática
    technique_id: T1057                # técnica ATT&CK
    technique_name: Process Discovery
    command: "tasklist (simulated)"    # NENHUMA execução real
  - time_offset: 4
    tactic: credential-access
    technique_id: T1003
    technique_name: OS Credential Dumping
    command: "Attempted LSASS access by tool (simulated)"
    metadata:
      target_process: "lsass.exe"
```

**Campos chave**:
- `id`, `name`, `description`: identificação do cenário.
- `host`, `user`: rótulos simples para compor o contexto.
- `events[]`: sequência temporal de eventos com `time_offset`, `tactic`, `technique_id`, `technique_name`, `command`, `metadata` opcional.

---

## Formato de Regras (YAML)

Regras simplificadas com três tipos de match: **equals**, **contains** e **regex**.  
**Semântica**: a regra **dispara** se **qualquer** cláusula indicada corresponder (OR lógico entre as cláusulas presentes).

```yaml
title: Possible OS Credential Dumping (Simulated)
id: R-CREDS-001
severity: high
tactic: credential-access
technique_id: T1003
technique_name: OS Credential Dumping
match:
  contains:
    - field: command
      value: LSASS
  # Exemplo de combinação:
  # equals:
  #   - field: tactic
  #     value: credential-access
  # regex:
  #   - field: command
  #     value: "(?i)lsass"
```

**Notas**:
- `match.equals|contains|regex` aceitam **um objeto** ou **lista** de `{field, value}`.
- `contains` é case-insensitive; `equals` é sensível; `regex` segue a expressão informada.

---

## Esquemas de Dados (JSONL)

### Eventos (logs) — `data/logs/*.jsonl`

```json
{
  "event_id": "c3c4a1f0-1d4e-4b1a-9c1b-0e1234567890",
  "timestamp": "2025-09-04T12:00:05Z",
  "host": "host-2",
  "user": "user2",
  "tactic": "credential-access",
  "technique_id": "T1003",
  "technique_name": "OS Credential Dumping",
  "command": "Attempted LSASS access by tool (simulated)",
  "simulated": true,
  "metadata": { "target_process": "lsass.exe" },
  "scenario_id": "SC-CREDS-001",
  "scenario_name": "Credential Access — OS Credential Dumping (Simulated)",
  "scenario_desc": "Cadeia de eventos..."
}
```

### Detecções — `data/detections/detections.jsonl`

```json
{
  "rule_id": "R-CREDS-001",
  "rule_title": "Possible OS Credential Dumping (Simulated)",
  "severity": "high",
  "tactic": "credential-access",
  "technique_id": "T1003",
  "technique_name": "OS Credential Dumping",
  "event_id": "c3c4a1f0-1d4e-4b1a-9c1b-0e1234567890",
  "timestamp": "2025-09-04T12:00:05Z",
  "host": "host-2",
  "user": "user2",
  "matched_fields": {
    "contains": [
      { "field": "command", "value": "LSASS" }
    ]
  },
  "scenario_id": "SC-CREDS-001",
  "scenario_name": "Credential Access — OS Credential Dumping (Simulated)"
}
```

---

## Relatórios

O comando `report` agrega e escreve `reports/YYYYMMDD_HHMM_report.md` contendo:
- **Cenários executados**
- **Técnicas vistas (MITRE ATT&CK)**
- **Alertas por regra** (com contagem)

> Observação: relatório consolida dados **sintéticos**. É possível estender para métricas como cobertura por tática/técnica, densidade de alertas e timeline.

---

## Fluxo de Trabalho Típico

1) **Simulação**:
```bash
python -m tacticlab.cli simulate -s scenarios/initial_access_phishing.yaml
python -m tacticlab.cli simulate -s scenarios/credential_dumping_sim.yaml
```

2) **Detecção**:
```bash
python -m tacticlab.cli detect -r rules/ -l data/logs
```

3) **Relatório**:
```bash
python -m tacticlab.cli report
# Abra o .md gerado em reports/
```

4) **Iterar**:
- Ajuste **regras** para reduzir falsos positivos.
- Crie **novos cenários** para outras táticas/técnicas (ATT&CK).

---

## Extensões e Roadmap

- **Novos cenários**: *Defense Evasion*, *C2*, *Exfiltration over Web Services*, *Scheduled Task*.
- **Exporters**: CSV/NDJSON compatíveis com **ELK**; conversor parcial para **Sigma**.
- **Dashboards**: importar JSONL no **Kibana/Grafana**.
- **Intelligence**: IOCs **fictícios** (IPs/domínios/hashes) e regras baseadas em IoCs.
- **Métricas**: cobertura por tática/técnica, densidade de alertas, timeline por cenário.
- **Testes**: suíte `pytest` para regras e parsing.
- **Conversores**: from/to Sigma (subset) e STIX-like **(somente sintético)**.

---

## Boas Práticas / Limitações

- **Seguro**: sem execução real; não altera registro/serviços/contas. Tudo é **texto**.
- **Didático**: reforça **processo** de SOC/Red Team (simular → detectar → reportar).
- **Não substitui** SIEM/EDR: laboratório para portfólio; sem correlação temporal avançada, estado de sessão ou UEBA.
- **Correspondência simples**: `equals`/`contains`/`regex` com lógica **OR**. Para AND/NOT/Agregações, estenda a engine.

---

## Contribuição

Contribuições são bem-vindas!
- Issues/PRs com melhorias de documentação, regras e cenários (sem payloads reais).
- Integrações com ELK/Grafana e exportadores.
- Padrão de commit: `feat: ...`, `fix: ...`, `docs: ...`, `test: ...`, `refactor: ...`.

---

## Autor

**Adriel (adrielck)**  
- GitHub: https://github.com/adrielck

---

## Licença

**MIT** — veja `LICENSE`.
