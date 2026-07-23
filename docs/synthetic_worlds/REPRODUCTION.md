# Reproduction

The candidate requires Python 3.10 or newer. Runtime generation and validation use only the standard library. The test command requires `pytest>=8,<9`.

From the candidate root:

```bash
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=. pytest -q tests
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=. python -m synthetic_worlds.cli validate-export EXPORT_MANIFEST.json
```

Generate and validate a fresh tiny dataset in a separate empty directory:

```bash
out="$(mktemp -d)/fixture"
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=. python -m synthetic_worlds.cli generate example_recipes/basic_world.json "$out" --shard-size 2
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=. python -m synthetic_worlds.cli validate "$out/DATASET_MANIFEST.json" "$out/shards" --recipe example_recipes/basic_world.json
```

External copy-out verification:

```bash
copy="$(mktemp -d)"
cp -a . "$copy/candidate"
cd "$copy/candidate"
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=. pytest -q tests
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=. python -m synthetic_worlds.cli validate-export EXPORT_MANIFEST.json
```

The committed example contains four records split across two tiny JSONL shards. The export manifest binds the exact file set, recipe, shard identities, privacy scan, qualification receipt, and human release state `NOT_REVIEWED`.
