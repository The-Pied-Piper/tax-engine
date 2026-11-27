"""The Quebec T1 birth year form: the year of birth entered once for Quebec's Schedule 8 line A.

Quebec does not import the federal T1 forms, so its own form declares the optional input
`ca/birth_year` ("Enter your date of birth in the "Step 1 - Identification and other information"
area on page 1 of your return.") and supplies it to the T1 holder's export that Schedule 8 reads.
"""

from __future__ import annotations

from typing import Any

import yaml

from tests.jurisdictions.ca_qc.conftest import QUEBEC_PARTS


def _load(name: str) -> Any:
    return yaml.safe_load((QUEBEC_PARTS / name).read_text(encoding="utf-8"))


def test_the_input_is_optional_with_no_default_and_cites_the_t1_identification_area() -> None:
    part = _load("t1_birth_year_inputs.yaml")

    assert part["form"] == {"name": "ca-qc/t1_birth_year"}
    (declared,) = part["inputs"]
    assert declared["name"] == "ca/birth_year"
    assert declared["required"] is False
    assert declared["default"] is None
    assert "Step 1 - Identification and other information" in declared["basis"]


def test_the_form_exports_the_year_and_supplies_it_to_the_t1_holders_record_list() -> None:
    form = _load("t1_birth_year.yaml")["form"]

    assert form["name"] == "ca-qc/t1_birth_year"
    assert form["exports"] == ["ca/birth_year"]
    assert form["supplies"] == {"ca/t1_lines_copied_by_provinces.birth_year": "ca/birth_year"}
