# Agent Pattern

The implementation uses supervisor-style multi-agent orchestration with a reflection/self-healing validation loop.

The supervisor/graph controls which specialist executes next. Structured Pydantic outputs create explicit handoff boundaries.

A reflection node validates critical state and can request a retry or stop with an explicit failure condition.
