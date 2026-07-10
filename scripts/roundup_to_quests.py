"""Render proposed quest drafts from a weekly roundup into a staging directory."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.append(str(ROOT))

from src.research import parse_roundup, quests_from_roundup, render_quest_markdown  # noqa: E402


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("roundup", type=Path)
    parser.add_argument("--out", type=Path, default=ROOT / "outputs" / "quest_staging")
    args = parser.parse_args()
    roundup = parse_roundup(args.roundup)
    quests = quests_from_roundup(roundup)
    ids = [quest.quest_id for quest in quests]
    if len(ids) != len(set(ids)):
        raise ValueError("roundup contains duplicate quest IDs")
    args.out.mkdir(parents=True, exist_ok=True)
    for quest in quests:
        slug = quest.title.lower().replace(" ", "-")
        path = args.out / f"{quest.quest_id.lower()}-{slug}.md"
        path.write_text(render_quest_markdown(quest))
        print(path)


if __name__ == "__main__":
    main()
