"""Every manifest step writes `name`, `title`, `reference` and `unit` first, in that order.

`docs/manifest-format.md` ("Capability selections") states this house order. The per-part shape
tests compare whole mappings, which ignore key order, so this one test walks every shipped
manifest part instead of each part repeating the check.
"""

from __future__ import annotations

from pathlib import Path

import yaml

import tax_engine.jurisdictions

LEADING = ("name", "title", "reference", "unit")
ROOT = Path(tax_engine.jurisdictions.__file__).parent


def _misordered() -> list[str]:
    found: list[str] = []
    for part in sorted(ROOT.rglob("manifests/**/*.yaml")):
        loaded = yaml.safe_load(part.read_text(encoding="utf-8"))
        if not isinstance(loaded, dict):
            continue
        for step in loaded.get("capabilities") or []:
            if not isinstance(step, dict):
                continue
            keys = list(step)
            leading = [key for key in keys if key in LEADING]
            if keys[: len(leading)] != leading or leading != [k for k in LEADING if k in leading]:
                found.append(f"{part.relative_to(ROOT)}: {keys}")
    return found


def test_every_manifest_step_writes_its_leading_keys_first_in_the_house_order() -> None:
    assert _misordered() == []
