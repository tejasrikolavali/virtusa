# Framework Decision

LangGraph is selected because the capstone explicitly requires it and because the workflow is stateful and conditional.

The design needs:
- typed shared state
- explicit graph topology
- conditional routing
- checkpointing
- resumable cases

CrewAI is not used because it is optional and would add another orchestration framework without helping satisfy the mandatory LangGraph requirements.
