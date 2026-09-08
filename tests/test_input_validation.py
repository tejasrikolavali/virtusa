import json

import pytest

from src.fraud_copilot.graph.builder import run_case


def test_rejects_order_with_missing_required_fields(tmp_path):
    path = tmp_path / "orders.json"
    path.write_text(json.dumps({"orders": [{"order_id": "ORDER-BAD"}]}), encoding="utf-8")

    with pytest.raises(ValueError, match="validation error"):
        run_case(path, "ORDER-BAD")