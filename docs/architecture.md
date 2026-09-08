# Architecture

LangGraph is the required orchestration framework.

Flow:
START → prepare/context → signal collection → risk scoring → conditional resolution → conditional escalation → reflection → finalize → END.

Workers:
- Signal collection
- Risk scoring
- Hold/resolution draft
- Escalation

Shared typed state is `FraudState`.

SQLite checkpointer persists graph state by `thread_id`. `pause_case()` returns
the interrupted state and `resume_case()` resumes it in a separate call;
`run_case()` keeps the convenience behavior of pausing and immediately resuming.

The design deliberately separates trusted structured order fields from quarantined free-text.
