"""Evaluate one ARCI JSON target and write a transparent result."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.append(str(ROOT))

from src.arci import ArciAssessment  # noqa: E402


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", type=Path, default=ROOT / "configs" / "arci_synthetic_target.json")
    parser.add_argument("--out", type=Path, default=ROOT / "outputs" / "qst_arci_0001")
    args = parser.parse_args()
    data = json.loads(args.config.read_text())
    result = ArciAssessment.from_dict(data).evaluate().to_dict()
    payload = {"target": data.get("target", "unknown"), "synthetic": True, "result": result}
    args.out.mkdir(parents=True, exist_ok=True)
    output = args.out / "arci_result.json"
    output.write_text(json.dumps(payload, indent=2))
    print(json.dumps(payload, indent=2))


if __name__ == "__main__":
    main()
