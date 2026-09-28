import argparse
import json
from pathlib import Path

from src.graph import process_dispute


def main():
    parser = argparse.ArgumentParser(description="Run the dispute triage copilot for a synthetic case.")
    parser.add_argument("--input", required=True, help="Path to the dispute JSON file.")
    args = parser.parse_args()

    data = json.loads(Path(args.input).read_text(encoding="utf-8"))
    result = process_dispute(data)
    print(json.dumps(result, indent=2, default=str))


if __name__ == "__main__":
    main()
