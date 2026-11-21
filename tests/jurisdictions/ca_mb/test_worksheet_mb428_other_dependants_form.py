"""The Manitoba forms `ca-mb/worksheet_mb428_other_dependants` and `..._total` (Worksheet MB428,
CRA 5007-D, 2025, section "Line 58729"): the form headers, the input part and the exports.

The column form runs once for each dependant ("Complete one column for each dependant."), exports
line 3 and takes lines 1 and 2 as the fields of its records. The total form holds line 4. Both share
the title of Worksheet MB428 with the basic personal amount form they are split from.
"""

from __future__ import annotations

import tax_engine.jurisdictions.ca_mb.catalog as mb
from tests.jurisdictions.ca_mb.mb428_dependants_support import (
    COLUMNS_FORM,
    LINE_1,
    LINE_2,
    LINE_3,
    LINE_4,
    TOTAL_FORM,
    load_part,
)
from tests.jurisdictions.ca_mb.support import manitoba_kinds
from tests.kinds import non_negative


def test_the_column_form_is_split_from_worksheet_mb428_and_shares_its_title() -> None:
    part = load_part("worksheet_mb428_other_dependants.yaml")

    assert list(part) == ["form", "capabilities"]
    assert part["form"]["name"] == COLUMNS_FORM
    assert part["form"]["title"] == "Worksheet MB428"
    assert part["form"]["required"] is True
    assert part["form"]["instances"] == COLUMNS_FORM
    assert part["form"]["min_instances"] == 0
    assert part["form"]["exports"] == [LINE_3]
    assert [field["name"] for field in part["form"]["fields"]] == [LINE_1, LINE_2]
    assert part["capabilities"] == []


def test_line_1_is_required_and_line_2_is_optional() -> None:
    line_1, line_2 = load_part("worksheet_mb428_other_dependants.yaml")["form"]["fields"]

    assert line_1["required"] is True
    assert line_2["required"] is False
    assert line_2["default"] is None


def test_the_input_part_names_the_form_and_declares_the_empty_default_list() -> None:
    part = load_part("worksheet_mb428_other_dependants_inputs.yaml")

    assert list(part) == ["form", "inputs"]
    assert part["form"] == {"name": COLUMNS_FORM}
    (declared,) = part["inputs"]
    assert declared["name"] == COLUMNS_FORM
    assert declared["required"] is False
    assert declared["default"] == []


def test_the_total_form_exports_line_4_and_shares_the_title() -> None:
    part = load_part("worksheet_mb428_other_dependants_total.yaml")

    assert part["form"] == {
        "name": TOTAL_FORM,
        "title": "Worksheet MB428",
        "required": True,
        "exports": [LINE_4],
    }


def test_the_lines_are_registered_non_negative_amounts() -> None:
    for identifier, declared in (
        (LINE_1, mb.WORKSHEET_MB428_OTHER_DEPENDANTS_LINE_1),
        (LINE_2, mb.WORKSHEET_MB428_OTHER_DEPENDANTS_LINE_2),
        (LINE_3, mb.WORKSHEET_MB428_OTHER_DEPENDANTS_LINE_3),
        (LINE_4, mb.WORKSHEET_MB428_OTHER_DEPENDANTS_LINE_4),
    ):
        kind = manitoba_kinds().kind(identifier)
        assert kind is declared
        assert non_negative(kind)


def test_the_list_kind_has_the_two_entered_lines_as_fields() -> None:
    kind = manitoba_kinds().kind(COLUMNS_FORM)

    assert kind is mb.WORKSHEET_MB428_OTHER_DEPENDANTS
    assert [field.identifier for field in mb.WORKSHEET_MB428_OTHER_DEPENDANTS.fields] == [
        LINE_1,
        LINE_2,
    ]
