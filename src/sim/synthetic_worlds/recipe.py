"""Declarative recipes, deterministic sampling, and preflight budgets."""
from __future__ import annotations

import hashlib
import itertools
import math
import random
from collections.abc import Iterator, Mapping, Sequence
from typing import Any

from .common import Budget, NAME_RE, RECIPE_SCHEMA, RECORD_SCHEMA, ValidationError, finite_number, load_json, stable_hash, stable_json

_REQUIRED = {"schema_version", "name", "seed", "parameters", "samplers", "records"}
_ALLOWED = _REQUIRED | {"description"}


class DeterministicRandom:
    def __init__(self, seed: int | str):
        if isinstance(seed, bool) or not isinstance(seed, (int, str)) or not str(seed):
            raise ValidationError("seed must be a non-empty string or integer")
        self.seed = str(seed)
        digest = hashlib.sha256(self.seed.encode()).hexdigest()
        self._rng = random.Random(int(digest[:16], 16))

    def uniform(self, low: float, high: float) -> float:
        return self._rng.uniform(low, high)

    def snapshot(self) -> dict[str, Any]:
        version, state, gauss = self._rng.getstate()
        return {"seed": self.seed, "version": version, "state_hash": stable_hash([state, gauss])}


def _scalar(value: Any, label: str) -> None:
    if value is None or isinstance(value, (str, bool, int)):
        return
    if isinstance(value, float) and math.isfinite(value):
        return
    raise ValidationError(f"{label} must be a finite JSON scalar")


def expand_parameter(spec: Any) -> list[Any]:
    if isinstance(spec, list):
        values = spec
    elif not isinstance(spec, Mapping):
        _scalar(spec, "parameter")
        return [spec]
    elif set(spec) == {"values"}:
        values = spec["values"]
        if not isinstance(values, list):
            raise ValidationError("parameter values must be a list")
    elif set(spec) == {"start", "stop", "step"}:
        start, stop, step = (finite_number(spec[key], f"parameter.{key}") for key in ("start", "stop", "step"))
        if step == 0 or (step > 0 and start > stop) or (step < 0 and start < stop):
            raise ValidationError("parameter range is invalid")
        count = int(math.floor((stop - start) / step + 1e-12)) + 1
        if not 1 <= count <= 1_000_000:
            raise ValidationError("parameter range size is invalid")
        return [round(start + index * step, 12) for index in range(count)]
    else:
        raise ValidationError("unsupported parameter specification")
    if not values:
        raise ValidationError("parameter values must be non-empty")
    for index, value in enumerate(values):
        _scalar(value, f"parameter[{index}]")
    return list(values)


def parameter_sweep(parameters: Mapping[str, Any], budget: Budget | None = None) -> Iterator[dict[str, Any]]:
    budget = budget or Budget(); budget.validate()
    keys = sorted(parameters)
    values = [expand_parameter(parameters[key]) for key in keys]
    total = math.prod(map(len, values)) if values else 1
    if total > budget.max_parameter_combinations:
        raise ValidationError("parameter sweep exceeds combination budget")
    for combination in itertools.product(*values):
        yield dict(zip(keys, combination))


def _bounds(value: Any) -> list[tuple[float, float]]:
    if not isinstance(value, list) or not value:
        raise ValidationError("bounds must be a non-empty list")
    result = []
    for item in value:
        if not isinstance(item, list) or len(item) != 2:
            raise ValidationError("each bound must be [low, high]")
        low, high = finite_number(item[0], "low"), finite_number(item[1], "high")
        if low > high:
            raise ValidationError("bound low exceeds high")
        result.append((low, high))
    return result


def _sampler_points(spec: Any) -> int:
    if not isinstance(spec, Mapping) or not isinstance(spec.get("name"), str) or not NAME_RE.fullmatch(spec["name"]):
        raise ValidationError("sampler must have a valid name")
    typ = spec.get("type")
    keys = {
        "spatial_grid": {"name", "type", "bounds", "counts"},
        "spatial_uniform": {"name", "type", "bounds", "n"},
        "temporal_sequence": {"name", "type", "start", "stop", "step"},
        "temporal_uniform": {"name", "type", "start", "stop", "n"},
    }
    if typ not in keys or set(spec) != keys[typ]:
        raise ValidationError("unsupported sampler or sampler keys")
    if typ == "spatial_grid":
        bounds, counts = _bounds(spec["bounds"]), spec["counts"]
        if not isinstance(counts, list) or len(counts) != len(bounds) or any(not isinstance(n, int) or isinstance(n, bool) or n < 1 for n in counts):
            raise ValidationError("grid counts are invalid")
        return math.prod(counts)
    if typ == "spatial_uniform":
        _bounds(spec["bounds"]); n = spec["n"]
    elif typ == "temporal_sequence":
        return len(expand_parameter({key: spec[key] for key in ("start", "stop", "step")}))
    else:
        low, high, n = finite_number(spec["start"], "start"), finite_number(spec["stop"], "stop"), spec["n"]
        if low > high:
            raise ValidationError("temporal start exceeds stop")
    if not isinstance(n, int) or isinstance(n, bool) or n < 1:
        raise ValidationError("sample count must be a positive integer")
    return n


def validate_recipe(recipe: Mapping[str, Any], budget: Budget | None = None) -> None:
    budget = budget or Budget(); budget.validate()
    keys = set(recipe)
    if _REQUIRED - keys:
        raise ValidationError(f"recipe missing required keys: {sorted(_REQUIRED - keys)}")
    if keys - _ALLOWED:
        raise ValidationError(f"recipe contains unknown keys: {sorted(keys - _ALLOWED)}")
    if recipe["schema_version"] != RECIPE_SCHEMA:
        raise ValidationError("recipe schema version mismatch")
    if not isinstance(recipe["name"], str) or not NAME_RE.fullmatch(recipe["name"]):
        raise ValidationError("recipe name is invalid")
    DeterministicRandom(recipe["seed"])
    records = recipe["records"]
    if not isinstance(records, int) or isinstance(records, bool) or not 1 <= records <= budget.max_records:
        raise ValidationError("records exceed budget or are invalid")
    parameters = recipe["parameters"]
    if not isinstance(parameters, Mapping) or any(not isinstance(name, str) or not NAME_RE.fullmatch(name) for name in parameters):
        raise ValidationError("parameters must be a named object")
    list(parameter_sweep(parameters, budget))
    samplers = recipe["samplers"]
    if not isinstance(samplers, list) or not samplers:
        raise ValidationError("samplers must be a non-empty list")
    names, points = set(), 0
    for spec in samplers:
        points += _sampler_points(spec)
        if spec["name"] in names:
            raise ValidationError("sampler names must be unique")
        names.add(spec["name"])
    if points > budget.max_points_per_record or points * records > budget.max_total_points:
        raise ValidationError("samplers exceed point budget")
    stable_json(recipe)


def load_recipe(path: str, budget: Budget | None = None) -> dict[str, Any]:
    recipe = load_json(path)
    if not isinstance(recipe, dict):
        raise ValidationError("recipe root must be an object")
    validate_recipe(recipe, budget)
    return recipe


def _samples(recipe: Mapping[str, Any], rng: DeterministicRandom) -> dict[str, Any]:
    result = {}
    for spec in recipe["samplers"]:
        typ = spec["type"]
        if typ == "spatial_grid":
            axes = []
            for (low, high), count in zip(_bounds(spec["bounds"]), spec["counts"]):
                axes.append([low] if count == 1 else [low + i * (high - low) / (count - 1) for i in range(count)])
            value = [list(point) for point in itertools.product(*axes)]
        elif typ == "spatial_uniform":
            value = [[rng.uniform(low, high) for low, high in _bounds(spec["bounds"])] for _ in range(spec["n"])]
        elif typ == "temporal_sequence":
            value = [float(item) for item in expand_parameter({key: spec[key] for key in ("start", "stop", "step")})]
        else:
            value = [rng.uniform(float(spec["start"]), float(spec["stop"])) for _ in range(spec["n"])]
        result[spec["name"]] = value
    return result


def generate_records(recipe: Mapping[str, Any], budget: Budget | None = None) -> Iterator[dict[str, Any]]:
    budget = budget or Budget(); validate_recipe(recipe, budget)
    rng, combinations = DeterministicRandom(recipe["seed"]), list(parameter_sweep(recipe["parameters"], budget))
    for record_id in range(recipe["records"]):
        record = {"schema_version": RECORD_SCHEMA, "record_id": record_id, "parameters": combinations[record_id % len(combinations)], "samples": _samples(recipe, rng), "rng": rng.snapshot()}
        record["record_hash"] = stable_hash(record)
        yield record


def preflight_write(recipe: Mapping[str, Any], shard_size: int, budget: Budget | None = None) -> dict[str, int]:
    budget = budget or Budget(); validate_recipe(recipe, budget)
    if not isinstance(shard_size, int) or isinstance(shard_size, bool) or shard_size < 1:
        raise ValidationError("shard_size must be positive")
    shards = math.ceil(recipe["records"] / shard_size)
    points = sum(_sampler_points(spec) for spec in recipe["samplers"])
    estimated = recipe["records"] * (512 + points * 96)
    if shards > budget.max_shards or estimated > budget.max_bytes:
        raise ValidationError("planned shards or bytes exceed budget")
    return {"records": recipe["records"], "shards": shards, "estimated_bytes": estimated}
