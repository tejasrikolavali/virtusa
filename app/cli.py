import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.fraud_copilot.graph.builder import run_case
from src.fraud_copilot.config import settings

def main():
    parser = argparse.ArgumentParser(description="Order Fraud & Chargeback Triage Copilot")
    sub = parser.add_subparsers(dest="command", required=True)

    demo = sub.add_parser("demo")
    demo.add_argument("--order-id", default="ORDER-001")

    run = sub.add_parser("run")
    run.add_argument("--order", required=True)
    run.add_argument("--order-id", default="ORDER-001")

    args = parser.parse_args()

    if args.command == "demo":
        order_path = Path(__file__).resolve().parents[1] / "data" / "orders" / "sample_orders.json"
        result = run_case(str(order_path), args.order_id)
    else:
        order_path = Path(args.order)
        if not order_path.is_absolute():
            order_path = Path.cwd() / order_path
        result = run_case(str(order_path), args.order_id)

    print("=" * 64)
    print("ORDER FRAUD & CHARGEBACK TRIAGE COPILOT")
    print("=" * 64)
    print(json.dumps(result, indent=2, default=str))
    print("=" * 64)

if __name__ == "__main__":
    main()
