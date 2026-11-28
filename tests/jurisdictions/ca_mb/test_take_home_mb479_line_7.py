"""Form MB479 (2025 (2025) line 7, the basic credit, over the optional year of birth.

Form text (CRA 5007-tc-25e.txt): "Line 7: Basic credit 195.00". The amount is the
`ca-mb/personal_tax_credit_basic` dataset, claimed through core/credit_amount.

The form prints no age condition. The Manitoba guide, CRA 5007-PC (Form MB479, Personal tax
credit): "If you were under 19 years of age at the end of the year, you can only claim this credit
if one of the following applies to you: You had a spouse or common-law partner / You were a parent
/ You can claim the Manitoba homeowners affordability tax credit on your 2025 return". The engine
models a filer with no spouse, child or property, so a filer under 19 at the end of the year has no
credit: line 7 is 0.00. The year of birth is the T1's optional `ca/birth_year`; a request that
leaves it out claims the credit in full. The cutoff year is 2006 (age 19 on 31 December 2025);
the 2026 cutoff is in the end-to-end test.

The test composes the real line 7 part and the T1 forms it reads over a test-local form declaration
(`age_support`), and types in only the salary and, in some tests, the year of birth.
"""

from __future__ import annotations

from decimal import Decimal
from pathlib import Path

import pytest
import yaml

from tax_engine.domain.artifact import Artifact
from tax_engine.jurisdictions.ca.catalog.personal_amounts import BIRTH_YEAR
from tax_engine.jurisdictions.ca_mb.catalog import MB479_BASIC_CREDIT_LINE_7
from tests.jurisdictions.ca_mb import age_support as s
from tests.jurisdictions.ca_mb.support import manitoba_kinds
from tests.kinds import non_negative

D = Decimal
FORM_NAME = "ca-mb/mb479"
LINES = ("mb479_line_7.yaml",)
LINE_7 = "ca-mb/mb479_basic_credit_line_7"


def _line_7(tmp_path: Path, salary: str, year: int | None) -> Decimal:
    given = () if year is None else (Artifact(BIRTH_YEAR, year),)
    return s.value(s.sheet(tmp_path, FORM_NAME, salary, LINES, (LINE_7,), given), LINE_7)


@pytest.mark.parametrize("salary", ["10000", "200000"])
@pytest.mark.parametrize("year", [None, 1955, 1980, 2006])
def test_line_7_is_the_printed_claim_when_19_or_older_or_the_year_is_left_out(
    tmp_path: Path, salary: str, year: int | None
) -> None:
    assert _line_7(tmp_path, salary, year) == D("195.00")


@pytest.mark.parametrize("salary", ["10000", "200000"])
@pytest.mark.parametrize("year", [2007, 2009, 2025])
def test_line_7_is_zero_when_under_19_at_the_end_of_2025(
    tmp_path: Path, salary: str, year: int
) -> None:
    assert _line_7(tmp_path, salary, year) == D("0.00")


def test_the_part_reads_the_flag_claims_the_dataset_figure_and_multiplies_them() -> None:
    part = yaml.safe_load((s.MB_PARTS / "mb479_line_7.yaml").read_text(encoding="utf-8"))

    assert part["form"] == {"name": FORM_NAME}
    flag, claim, line = part["capabilities"]
    assert flag["name"] == "core/first_record_count"
    assert flag["consumes"] == {"records": "ca/t1_lines_copied_by_provinces.age_19_or_older"}
    assert flag["produces"] == {"output": "ca-mb/mb479_age_19_or_older"}
    assert claim["name"] == "core/credit_amount"
    assert claim["params"] == {"amount": "ca-mb/personal_tax_credit_basic"}
    assert claim["produces"] == {"output": "ca-mb/mb479_basic_credit_claim_line_7"}
    assert line["name"] == "core/times_count"
    assert line["title"] == "Basic credit"
    assert line["reference"] == "7"
    assert line["unit"] == "ca/cad"
    assert line["blank"] == {"count": "1"}
    assert line["produces"] == {"output": LINE_7}


def test_the_basic_credit_is_a_non_negative_amount_kind() -> None:
    kind = manitoba_kinds().kind(LINE_7)

    assert kind is MB479_BASIC_CREDIT_LINE_7
    assert non_negative(kind)
