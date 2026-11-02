"""Which counts of the CA-ON manifest `ca/count_without_records` lets the filer leave blank.

`05j_cpp_lines.yaml` checks Schedule 8 Part 4 and Part 5 completed against the copies of Form RC381.
Both parts say "If not, leave this part blank", so a blank count is passed on as a blank count; a
filled count above 0 with a copy of the form is still refused by the class.
"""

from __future__ import annotations

from pathlib import Path

import yaml

import tax_engine.jurisdictions.ca_on

PART = (
    Path(tax_engine.jurisdictions.ca_on.__file__).parent / "manifests" / "v1" / "05j_cpp_lines.yaml"
)


def steps() -> list[dict[str, object]]:
    document = yaml.safe_load(PART.read_text(encoding="utf-8"))
    return [step for step in document["capabilities"] if step["name"] == "ca/count_without_records"]


def test_both_guards_pass_a_blank_count_on() -> None:
    found = steps()

    assert len(found) == 2
    assert all(step.get("blank") == {"count": "pass_on"} for step in found)
