#!/usr/bin/env python3
"""Meta-validate every extension schema and verify its $id matches the path it is
served at on GitHub Pages, and that the self-reference const matches the $id.

Run from the repository root:  python3 scripts/verify_ids.py
"""
import glob
import json
import os
import sys

from jsonschema import Draft7Validator

BASE_URL = "https://opencosmos.github.io/stac-extensions"

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def self_reference_const(schema):
    """Return the const inside properties.stac_extensions.contains, if present."""
    try:
        return schema["properties"]["stac_extensions"]["contains"]["const"]
    except (KeyError, TypeError):
        return None


def main():
    errors = []
    paths = sorted(glob.glob(os.path.join(ROOT, "*", "v*", "schema.json")))
    if not paths:
        print("No schema.json files found", file=sys.stderr)
        return 1

    for path in paths:
        rel = os.path.relpath(path, ROOT).replace(os.sep, "/")
        expected_id = f"{BASE_URL}/{rel}"
        with open(path, encoding="utf-8") as fh:
            schema = json.load(fh)

        try:
            Draft7Validator.check_schema(schema)
        except Exception as exc:  # noqa: BLE001
            errors.append(f"{rel}: invalid JSON Schema: {exc}")
            continue

        if schema.get("$id") != expected_id:
            errors.append(
                f"{rel}: $id is {schema.get('$id')!r}, expected {expected_id!r}"
            )

        const = self_reference_const(schema)
        if const is not None and const != schema.get("$id"):
            errors.append(
                f"{rel}: stac_extensions const {const!r} does not match $id "
                f"{schema.get('$id')!r}"
            )

        print(f"OK  {rel}")

    if errors:
        print("\nFAILURES:", file=sys.stderr)
        for e in errors:
            print(f"  - {e}", file=sys.stderr)
        return 1

    print(f"\nAll {len(paths)} schemas valid and $id URLs consistent.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
