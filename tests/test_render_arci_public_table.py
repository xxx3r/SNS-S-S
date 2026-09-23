from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest

from scripts.render_arci_public_table import render_table


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "outputs/qst_arci_0001/synthetic_target_sensitivity.json"
SCRIPT = ROOT / "scripts/render_arci_public_table.py"


def test_committed_arci_public_table_is_reproducible(tmp_path: Path) -> None:
    output = tmp_path / "table.md"
    subprocess.run(
        [sys.executable, str(SCRIPT), str(SOURCE), "--output", str(output)],
        cwd=ROOT,
        check=True,
    )
    assert output.read_text(encoding="utf-8") == (
        ROOT / "docs/public/generated/arci_sensitivity_table.md"
    ).read_text(encoding="utf-8")


def test_renderer_fails_closed_on_non_synthetic_input() -> None:
    payload = json.loads(SOURCE.read_text(encoding="utf-8"))
    payload["synthetic"] = False
    with pytest.raises(ValueError, match="synthetic evidence only"):
        render_table(payload)
