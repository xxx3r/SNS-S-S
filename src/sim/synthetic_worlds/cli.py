"""Command-line boundary for standalone synthetic-world generation and validation."""
from __future__ import annotations

import argparse
from pathlib import Path

from .core import (
    Budget,
    build_dataset_manifest,
    generate_records,
    load_json,
    load_recipe,
    preflight_write,
    stable_json,
    validate_dataset_manifest,
    validate_export_manifest,
    write_shards,
)


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Generate and validate bounded synthetic-world artifacts")
    commands = parser.add_subparsers(dest="command", required=True)
    generate = commands.add_parser("generate", help="generate a bounded dataset bundle")
    generate.add_argument("recipe")
    generate.add_argument("out_dir")
    generate.add_argument("--shard-size", type=int, default=1_000)
    validate = commands.add_parser("validate", help="validate a generated dataset bundle")
    validate.add_argument("manifest")
    validate.add_argument("shard_dir")
    validate.add_argument("--recipe")
    validate_export = commands.add_parser("validate-export", help="validate the complete export candidate")
    validate_export.add_argument("manifest")
    validate_export.add_argument("--root")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    if args.command == "generate":
        recipe = load_recipe(args.recipe)
        budget = Budget()
        preflight_write(recipe, args.shard_size, budget)
        output = Path(args.out_dir)
        output.mkdir(parents=True, exist_ok=True)
        shard_manifest = write_shards(
            generate_records(recipe, budget),
            output / "shards",
            args.shard_size,
            budget,
            expected_records=recipe["records"],
        )
        manifest = build_dataset_manifest(recipe, shard_manifest)
        (output / "DATASET_MANIFEST.json").write_text(stable_json(manifest) + "\n", encoding="utf-8")
        return 0
    if args.command == "validate":
        manifest = load_json(args.manifest)
        recipe = load_recipe(args.recipe) if args.recipe else None
        validate_dataset_manifest(manifest, args.shard_dir, recipe)
        return 0
    validate_export_manifest(args.manifest, args.root)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
