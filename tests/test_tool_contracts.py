from mcp_server.server import prior_disputes, transaction_lookup


def test_transaction_lookup_contract():
    result = transaction_lookup("TXN-001")
    assert isinstance(result, dict)
    assert "transaction_id" in result
    assert result["transaction_id"] == "TXN-001"


def test_unknown_transaction_error_path():
    result = transaction_lookup("DOES-NOT-EXIST")
    assert result.get("error") == "NOT_FOUND"


def test_prior_disputes_contract():
    result = prior_disputes("CUSTOMER-001")
    assert isinstance(result, list)
    assert result[0]["customer_id"] if result else True


def test_tool_response_schema_is_stable():
    result = transaction_lookup("TXN-002")
    assert {"transaction_id", "customer_id", "amount", "merchant", "status"}.issubset(set(result.keys()))
