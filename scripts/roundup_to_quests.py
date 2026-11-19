"""Stage semantic quest-action proposals from a weekly roundup."""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.append(str(ROOT))

from src.research import parse_roundup, quest_actions_from_roundup, render_quest_markdown, render_refinement_markdown  # noqa: E402

QUEST_RE = re.compile(r"QST-[A-Z0-9]+-[0-9]{4}")


def queue_ids(directory: Path) -> set[str]:
    result: set[str] = set()
    if not directory.exists():
        return result
    for path in directory.glob("*.md"):
        match = QUEST_RE.search(path.name)
        if match:
            result.add(match.group(0))
    return result


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("roundup", type=Path)
    parser.add_argument("--out", type=Path, default=ROOT / "outputs" / "quest_staging")
    args = parser.parse_args()

    active = queue_ids(ROOT / "quests/active")
    all_ids = set().union(
        active,
        queue_ids(ROOT / "quests/completed"),
        queue_ids(ROOT / "quests/proposed"),
        queue_ids(ROOT / "quests/blocked"),
    )
    roundup = parse_roundup(args.roundup)
    actions = quest_actions_from_roundup(roundup, active_quest_ids=active, all_quest_ids=all_ids)
    # Plan the complete proposal-only batch before writing any artifact.
    # Event IDs are intentionally unique, but proposal Markdown paths are
    # stable. Never allow a subsequent invocation to replace earlier evidence.
    planned: list[tuple[Path, str]] = []
    for action in actions:
        event_path = args.out / f"{action.quest_action_id}.json"
        event_content = json.dumps(action.as_event(), indent=2, sort_keys=True) + "\n"
        slug = action.quest.title.lower().replace(" ", "-")
        if action.action_type == "propose_new":
            proposal_path = args.out / f"{action.quest.quest_id.lower()}-{slug}.md"
            proposal_content = render_quest_markdown(action.quest)
        else:
            proposal_path = args.out / f"refine-{action.quest.quest_id.lower()}-{slug}.md"
            proposal_content = render_refinement_markdown(action)
        planned.extend(((event_path, event_content), (proposal_path, proposal_content)))

    paths = [path for path, _ in planned]
    if len(paths) != len(set(paths)):
        raise ValueError("staging batch contains duplicate output paths")
    for path in paths:
        if path.exists():
            raise FileExistsError(f"staging output already exists: {path}")

    args.out.mkdir(parents=True, exist_ok=True)
    for path, content in planned:
        # Exclusive creation also prevents overwrites if another process races.
        with path.open("x", encoding="utf-8") as stream:
            stream.write(content)
        print(path)


if __name__ == "__main__":
    main()
