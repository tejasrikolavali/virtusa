# Transaction Dispute & Fraud-Triage Copilot

Business Case: BC-AAIE-HACK-03 | Banking & Finance

This is a Python 3.11+ capstone starter matching the required repository structure.
`TODO` items are intentionally incomplete. Do not submit until implementation and
machine-generated evidence are produced.

## Setup (Windows PowerShell)
```powershell
py -3.11 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
copy .env.example .env
```

Set `GOOGLE_API_KEY` in `.env`. Never commit `.env`.

## Run
```powershell
python -m src.cli --input data/sample_inputs/dispute_001.json
pytest -q
python scripts/check_submission.py
```

## Local Phoenix collector
Start the local Phoenix collector in one terminal:
```powershell
python -m phoenix.server.main serve --host 127.0.0.1 --port 6006
```

Then run the synthetic dispute and regenerate the committed evidence in a second terminal:
```powershell
$env:PHOENIX_COLLECTOR_ENDPOINT = "http://127.0.0.1:6006"
$env:PHOENIX_PROJECT_NAME = "transaction-dispute-fraud-triage"
python -m src.cli --input data/sample_inputs/dispute_001.json
python scripts/run_all_evidence.py
```

The Phoenix exporter writes local span evidence to `traces/phoenix_spans.jsonl` and keeps the JSONL exporter attached for repo evidence even when a live Phoenix collector is not available.

## Final evidence regeneration
The final repository must have one documented command that regenerates the copilot,
Phoenix traces, tool/audit logs, evaluation, golden signals and dashboard. The
starter command is:
```powershell
python scripts/run_all_evidence.py
```

## Required architecture
LangGraph supervisor + 3 workers (classification, fraud scoring, chargeback/RAG),
conditional routing, SQLite checkpointing, structured outputs, MCP (2 tools + 1
resource), context write/select/compress/isolate, quarantine, tiered memory,
agentic RAG, Phoenix/OpenTelemetry, tool logging, guardrails, audit, governance,
DeepEval/LLM-as-judge and agent tests.

See `docs/IMPLEMENTATION_CHECKLIST.md` for AC-01–AC-12 and NFR-01–NFR-06.
