# NFR Evidence Checklist

NFR-01: `.env` is ignored; `.env.example` is committed.
NFR-02: README documents a one-command demo and sample input.
NFR-03: customer/order free-text is quarantined with trusted=false.
NFR-04: `logs/agent_runs/*.jsonl` contains structured events after a run.
NFR-05: all included order and knowledge data is synthetic.
NFR-06: framework and MCP decisions are documented.
NFR-07: reflection provides retry/explicit failure; MCP demo captures integration failures.
NFR-08: compressor.py implements long-thread summarization.
