"""NS428 (2025) line 58, the minimum tax carryover.

Form text (Form NS428, CRA 5003-C, confirmed 26 Nov 2026 from CRA's PDF): "Nova Scotia minimum tax
carryover: Amount from line 40427 of your return multiplied by 57.5%" (line 61540). The amount is
a record total of the T1's line 40427 export; the printed 57.5% is a dataset rate, rounded
half-up to the cent. A salary-only caller has no carryover, so the line is 0.00.
"""

from __future__ import annotations

from decimal import Decimal
from pathlib import Path

import pytest

import tax_engine.jurisdictions.ca_ns.catalog as ns_catalog
from tax_engine.domain.kinds import AmountKind
from tax_engine.domain.parameters.rate import RATE, Rate
from tax_engine.domain.parameters.rounding import RoundingMode, RoundTo
from tests.jurisdictions.ca_ns import ns428_tax_support as s
from tests.jurisdictions.ca_ns.ns428_credits_support import parameter_source
from tests.jurisdictions.ca_ns.support import nova_scotia_kinds
from tests.kinds import non_negative

D = Decimal


@pytest.mark.parametrize("salary", ["20000", "70000"])
def test_a_salary_only_caller_has_a_carryover_of_0(tmp_path: Path, salary: str) -> None:
    assert str(s.line(tmp_path, salary, s.LINE_58)) == "0.00"


@pytest.mark.parametrize(
    ("amount", "expected"),
    [
        # 1000.00 x 57.5% = 575.00.
        ("1000.00", "575.00"),
        # 0.01 x 57.5% = 0.00575, rounded half-up to the cent.
        ("0.01", "0.01"),
        # 0.08 x 57.5% = 0.046, rounded to the cent.
        ("0.08", "0.05"),
    ],
)
def test_line_58_is_57_point_5_percent_of_the_amount_rounded_half_up(
    tmp_path: Path, amount: str, expected: str
) -> None:
    given = {s.CARRYOVER: amount}

    assert str(s.line(tmp_path, "70000", s.LINE_58, given)) == expected
    assert s.line(tmp_path / "amount", "70000", s.LINE_58_AMOUNT, given) == D(amount)


def test_the_rate_dataset_is_57_point_5_percent_half_up_citing_the_form() -> None:
    data = parameter_source().get(s.RATE, 2025, RATE)

    assert data.values == Rate(D("0.575"))
    assert data.rounding == RoundTo(D("0.01"), RoundingMode.HALF_UP)
    assert data.sources == (
        "https://www.canada.ca/content/dam/cra-arc/formspubs/pbg/5003-c/5003-c-25e.txt",
    )


def test_the_part_is_a_record_total_of_the_t1_export_then_the_rate() -> None:
    part = s.part("ns428_line_58.yaml")

    assert list(part) == ["form", "capabilities"]
    assert part["form"] == {"name": "ca-ns/ns428"}
    assert part["capabilities"] == [
        {
            "name": "core/record_total",
            "title": "Amount from line 40427 of your return",
            "reference": "58 box A",
            "unit": "ca/cad",
            "consumes": {
                "records": "ca/t1_lines_copied_by_provinces.minimum_tax_carryover_line_40427"
            },
            "produces": {"output": s.LINE_58_AMOUNT},
        },
        {
            "name": "core/apply_rate",
            "title": "Nova Scotia minimum tax carryover",
            "reference": "58 box B",
            "unit": "ca/cad",
            "params": {"rate": s.RATE},
            "consumes": {"base": s.LINE_58_AMOUNT},
            "produces": {"output": s.LINE_58},
        },
    ]


def test_the_kind_is_a_registered_non_negative_amount_kind() -> None:
    kind = nova_scotia_kinds().kind(s.LINE_58)

    assert isinstance(kind, AmountKind)
    assert non_negative(kind)
    assert kind is ns_catalog.NS428_MINIMUM_TAX_CARRYOVER_LINE_58


def test_the_amount_kind_is_a_registered_non_negative_amount_kind() -> None:
    kind = nova_scotia_kinds().kind(s.LINE_58_AMOUNT)

    assert kind is ns_catalog.NS428_MINIMUM_TAX_CARRYOVER_AMOUNT_LINE_58
    assert non_negative(kind)
