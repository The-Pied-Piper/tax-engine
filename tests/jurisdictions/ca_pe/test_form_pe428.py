"""The Prince Edward Island form `ca-pe/pe428` (Form PE428, CRA 5002-C): its name, its title as
printed, and its exports: line 5 (the bracket rate), worksheet line 4 of the age amount and line 10
before the printed maximum check (which tell the marginal rate whether the age amount is falling),
line 84 (the income over the base amount) and
line 87 (the low-income tax reduction), which the return summary's marginal rate reads, and
line 97, the Prince Edward Island tax, which the form supplies as `ca/provincial_tax.amount` for
T1 line 42800 (the copy lines 55, 58, 73, 74 and 82 have no step, and the lines after them read
the lines they copy directly).

The part file names the form and its exports; line parts carry the capabilities. The part is
read as YAML and composed here with the real line parts, and the kinds come from the Prince
Edward Island package list in `support.py`."""

from __future__ import annotations

from decimal import Decimal
from typing import Any

import pytest
import yaml

from tax_engine.domain.kinds import AmountKind
from tests.jurisdictions.ca_pe import pe428_support as s
from tests.jurisdictions.ca_pe.conftest import TakeHomeService
from tests.jurisdictions.ca_pe.credits_support import ALL_PARTS, HEADER, compute, value
from tests.jurisdictions.ca_pe.support import prince_edward_island_kinds
from tests.kinds import non_negative

D = Decimal
PART = s.PE_PARTS / "pe428.yaml"
LINE_5 = "ca-pe/pe428_bracket_rate_line_5"
LINE_84 = "ca-pe/pe428_income_over_base_amount_line_84"
LINE_87 = "ca-pe/pe428_low_income_tax_reduction_line_87"
LINE_97 = "ca-pe/pe428_prince_edward_island_tax_line_97"
AGE_LINE_4 = "ca-pe/worksheet_pe428_age_amount_line_4"
AGE_CLAIMED = "ca-pe/pe428_age_amount_claimed_line_10"
EXPORTS = [LINE_5, AGE_LINE_4, AGE_CLAIMED, LINE_84, LINE_87, LINE_97]
ALL_LINES = (1, 3, 4, 5, 6, 7, 8)


def _part() -> dict[str, Any]:
    part = yaml.safe_load(PART.read_text(encoding="utf-8"))
    assert isinstance(part, dict)
    return part


def test_the_form_is_named_titled_as_printed_and_required() -> None:
    form = _part()["form"]

    assert form["name"] == s.FORM_NAME
    assert form["title"] == "Form PE428: Prince Edward Island Tax and Credits"
    assert form["required"] is True


def test_the_form_exports_the_line_5_age_amount_84_87_and_97_figures() -> None:
    assert _part()["form"]["exports"] == EXPORTS


def test_the_form_supplies_line_97_as_the_provincial_tax_and_declares_no_capabilities() -> None:
    part = _part()

    assert part["form"]["supplies"] == {"ca/provincial_tax.amount": LINE_97}
    assert list(part["form"]) == ["name", "title", "required", "exports", "supplies"]
    assert list(part) == ["form", "capabilities"]
    assert part["capabilities"] == []


@pytest.mark.parametrize("identifier", EXPORTS)
def test_each_export_is_a_registered_non_negative_amount_kind(identifier: str) -> None:
    kinds = prince_edward_island_kinds()

    assert identifier in kinds.identifiers()
    kind = kinds.kind(identifier)
    assert isinstance(kind, AmountKind)
    assert non_negative(kind)


@pytest.mark.parametrize(
    ("salary", "line_84", "line_87", "line_97"),
    [
        ("20000", "0.00", "350.00", "33.83"),
        ("30000", "7085.00", "0.00", "1261.72"),
        ("70000", "46685.00", "0.00", "6355.92"),
    ],
)
def test_the_real_form_part_and_all_line_parts_compose_to_lines_84_87_and_97(
    take_home_service: TakeHomeService, salary: str, line_84: str, line_87: str, line_97: str
) -> None:
    service = take_home_service(HEADER, PART.read_text(encoding="utf-8"), *ALL_PARTS)
    sheet = compute(service, salary)

    assert value(sheet, LINE_84) == D(line_84)
    assert value(sheet, LINE_87) == D(line_87)
    assert value(sheet, LINE_97) == D(line_97)
