"""The Quebec take-home manifest asks the caller for the gross salary only.

The Quebec T1 employment income form's part `t1_employment_income_line_10100_inputs.yaml` declares
the one input of T1 line 10100, employment income (the input belongs to that form; the other forms
read its export). Both returns take the gross salary as their first income line (5005-R line 1 and
TP-1 line 101). The Quebec manifest is not complete until the later line tickets land, so this test
reads the part. The end-to-end ticket can move these checks onto the built manifest.
"""

from __future__ import annotations

from typing import Any

import yaml

from tests.manifest_support import QC_T1_LINE_10100_INPUT

PART = QC_T1_LINE_10100_INPUT


def _inputs() -> list[dict[str, Any]]:
    part = yaml.safe_load(PART.read_text(encoding="utf-8"))
    assert isinstance(part, dict)
    assert list(part) == ["form", "inputs"]
    assert part["form"] == {"name": "ca-qc/t1_employment_income"}
    return list(part["inputs"])


def test_the_salary_is_the_only_required_input() -> None:
    required = [declaration["name"] for declaration in _inputs() if declaration["required"]]

    assert required == ["ca/employment_income"]
    assert len(_inputs()) == 1


def test_the_salary_input_is_the_printed_employment_income_in_canadian_dollars() -> None:
    assert _inputs()[0] == {
        "name": "ca/employment_income",
        "title": "Employment income",
        "reference": "10100",
        "unit": "ca/cad",
        "required": True,
        "whole_cents": True,
    }
    assert list(_inputs()[0]) == [
        "name",
        "title",
        "reference",
        "unit",
        "required",
        "whole_cents",
    ]
