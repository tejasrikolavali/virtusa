# MCP Integration Decision

MCP is used because the case study explicitly requires a custom MCP server consumed by the agent.

The server exposes:
- `order_lookup`
- `payment_check`
- `fraud://policy-catalog` resource

The client uses `langchain-mcp-adapters`.

Why not direct database access?
The case requires interoperability evidence and an MCP tool/resource boundary. No external database is needed.

Why not A2A?
A2A is optional in the case study; MCP directly satisfies the required domain-tool interoperability requirement.
