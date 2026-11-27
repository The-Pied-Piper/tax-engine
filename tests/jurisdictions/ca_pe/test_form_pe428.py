"""The Prince Edward Island form `ca-pe/pe428` (Form PE428, CRA 5002-C) as declared so far: its
name, its title as printed, and the exports the return summary's marginal rate reads, line 84
(the income over the base amount) and line 87 (the low-income tax reduction), and line 88, the
tax after the reduction, exported until line 90 reads it (the copy lines 55, 58, 73, 74 and 82
have no step, and the lines after them read the lines they copy directly).

The part file names the form and its exports; line parts carry the capabilities. The Prince
Edward Island package is not yet listed, so the part is read as YAML and composed here with the
real line parts, and the kinds come from the Prince Edward Island package list in `support.py`."""

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
LINE_84 = "ca-pe/pe428_income_over_base_amount_line_84"
LINE_87 = "ca-pe/pe428_low_income_tax_reduction_line_87"
LINE_88 = "ca-pe/pe428_tax_line_88"
EXPORTS = [LINE_84, LINE_87, LINE_88]
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


def test_the_form_exports_lines_84_87_and_88() -> None:
    assert _part()["form"]["exports"] == EXPORTS


def test_the_form_supplies_nothing_and_the_part_declares_no_capabilities() -> None:
    part = _part()

    assert "supplies" not in part["form"]
    assert list(part["form"]) == ["name", "title", "required", "exports"]
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
    ("salary", "line_84", "line_87", "line_88"),
    [
        ("20000", "0.00", "350.00", "33.83"),
        ("30000", "7085.00", "0.00", "1261.72"),
        ("70000", "46685.00", "0.00", "6355.92"),
    ],
)
def test_the_real_form_part_and_all_line_parts_compose_to_lines_84_87_and_88(
    take_home_service: TakeHomeService, salary: str, line_84: str, line_87: str, line_88: str
) -> None:
    service = take_home_service(HEADER, PART.read_text(encoding="utf-8"), *ALL_PARTS)
    sheet = compute(service, salary)

    assert value(sheet, LINE_84) == D(line_84)
    assert value(sheet, LINE_87) == D(line_87)
    assert value(sheet, LINE_88) == D(line_88)
