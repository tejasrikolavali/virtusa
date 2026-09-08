# Memory Policy

Tier 1: working memory attached to the current case/session.

Tier 2: persistent long-term memory stored in SQLite metadata. Retrieval uses
deterministic case and text matching so it remains reproducible without an
external database service.

Persistence is verified by `tests/test_ac07_cross_session.py`.

Eviction:
1. Expired TTL records are deleted.
2. If the collection exceeds the maximum count, lower-importance records are removed first.
3. Among equal importance, least-recently-used records are removed first.

High-importance fraud case facts are retained longer than temporary facts.
