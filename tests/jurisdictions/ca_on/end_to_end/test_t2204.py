"""T2204 (2025, Employee Overpayment of Employment Insurance Premiums) from the salary alone: the
form's real parts composed end to end.

Every line part has its own test with its neighbours typed in. This module composes the whole form:
it copies every `t2204*.yaml` part, plus `salary.yaml`, from the package into a temporary manifest
folder beside a test-only header, and types in only the gross salary (`ca/employment_income`), plus
the given line 4 figure in one case. The real header is not used because its output, T1 line 167,
is not built yet. This is not a worked return: no return file, no slips, one form.

The form's exports are line 4 (the premiums deducted), the T1 line 45000 amount and line 16.

Form text: CRA T2204 (2025), line 1 "Total EI insurable earnings (box 24 or, if blank, box 14 of
your T4 slips)"; line 3 "Line 1 plus line 2 (maximum $65,700)"; line 7 "Amount from line 3 –
$2,000 = (if negative, enter "0")"; line 10 "Residents of other than Quebec Amount from line 1 ×
1.64% = (maximum $1,077.48)"; line 15 "Employment insurance overpayment: Enter whichever
is less: amount from line 9 or line 14. If this amount is more than $1, enter it on line 45000 of
your return."; line 16 "Non-refundable tax credit for employment insurance premiums through
employment: Enter whichever amount is the least: line 7, line 9 or line 12."; note (1) "If you
have no self-employment earnings and your total EI insurable earnings on your T4 slips are less
than $2,000, enter "0"."
The expected figures are the ones the full-form audit produced from this same composition.
"""

from __future__ import annotations

from decimal import Decimal
from textwrap import dedent

import pytest

from tax_engine.domain.artifact import Artifact
from tax_engine.domain.errors import NegativeArtifactError
from tax_engine.domain.jurisdiction_code import JurisdictionCode
from tax_engine.domain.kinds import AmountKind, CountKind
from tax_engine.domain.worksheet import Worksheet
from tax_engine.jurisdictions.ca.catalog.income import EMPLOYMENT_INCOME
from tax_engine.jurisdictions.ca.catalog.refund import (
    EI_OVERPAYMENT,
    T2204_LINE_1,
    T2204_LINE_1_COUNT,
    T2204_LINE_1_PLUS_2,
    T2204_LINE_3,
    T2204_LINE_6,
    T2204_LINE_7,
    T2204_LINE_8,
    T2204_LINE_10,
    T2204_LINE_13,
    T2204_LINE_14,
    T2204_LINE_15,
    T2204_LINE_15_COUNT,
    T2204_LINE_16,
    T2204_PREMIUMS_DEDUCTED,
    T2204_PREMIUMS_DEDUCTED_GIVEN,
)
from tests.jurisdictions.ca_on.conftest import TAKE_HOME, TakeHomeService

D = Decimal
HEADER = dedent("""\
    jurisdiction: CA-ON
    version: 1
    valid_from_tax_year: 2025
    outputs:
      - ca/employment_income
    capabilities: []
    """)
# The real T2204 declaration (`t2204.yaml`) carries the form and its exports, so the fixture's own
# form text is an empty mapping.
FORM = "{}\n"
PARTS = ("salary.yaml", *(part.name for part in sorted(TAKE_HOME.rglob("t2204*.yaml"))))

# Amount lines by form line; the line 1 count (note (1)) and line 15 count (more than $1) are
# counts and are read by their own kinds.
AMOUNT_LINES: dict[str, AmountKind] = {
    "1": T2204_LINE_1,
    "3": T2204_LINE_3,
    "4": T2204_PREMIUMS_DEDUCTED,
    "6": T2204_LINE_6,
    "7": T2204_LINE_7,
    "8": T2204_LINE_8,
    "10": T2204_LINE_10,
    "13": T2204_LINE_13,
    "14": T2204_LINE_14,
    "15": T2204_LINE_15,
    "16": T2204_LINE_16,
    "45000": EI_OVERPAYMENT,
}
COUNT_LINES: dict[str, CountKind] = {
    "1": T2204_LINE_1_COUNT,
    "15": T2204_LINE_15_COUNT,
}
CENT_LINES = ("3", "4", "10")


def compose(
    take_home_service: TakeHomeService, *given: Artifact[Decimal] | Artifact[int]
) -> Worksheet:
    worksheets = take_home_service(HEADER, FORM, *PARTS).compute(
        JurisdictionCode("CA-ON"), 2025, *given
    )
    (sheet,) = worksheets["ca/t2204"]
    return sheet


def salary_only(take_home_service: TakeHomeService, salary: str) -> Worksheet:
    return compose(take_home_service, Artifact(EMPLOYMENT_INCOME, D(salary)))


def amounts(sheet: Worksheet, expected: dict[str, str]) -> dict[str, Decimal]:
    return {line: sheet.get(AMOUNT_LINES[line]).value for line in expected}


def counts(sheet: Worksheet, expected: dict[str, int]) -> dict[str, int]:
    return {line: sheet.get(COUNT_LINES[line]).value for line in expected}


# Each salary's printed figures; a line left out of a case is not pinned by that case.
SALARY_70K_AMOUNTS = {
    "1": "70000",
    "3": "65700.00",
    "4": "1077.48",
    "6": "1077.48",
    "7": "63700.00",
    "8": "0",
    "10": "1077.48",
    "13": "0",
    "14": "0",
    "15": "0",
    "16": "1077.48",
    "45000": "0",
}
SALARY_30K_AMOUNTS = {
    "1": "30000",
    "3": "30000.00",
    "4": "492.00",
    "6": "492.00",
    "7": "28000.00",
    "8": "0",
    "10": "492.00",
    "13": "0",
    "14": "0",
    "15": "0",
    "16": "492.00",
    "45000": "0",
}
SALARY_2010_AMOUNTS = {
    "1": "2010",
    "3": "2010.00",
    "4": "32.96",
    "6": "32.96",
    "7": "10.00",
    "8": "22.96",
    "10": "32.96",
    "13": "0",
    "14": "22.96",
    "15": "22.96",
    "45000": "22.96",
    "16": "10.00",
}
SALARY_2032_AMOUNTS = {
    "4": "33.32",
    "7": "32.00",
    "8": "1.32",
    "15": "1.32",
    "45000": "1.32",
    "16": "32.00",
}
SALARY_2033_AMOUNTS = {"15": "0.34", "45000": "0", "16": "33.00"}
SALARY_1000_AMOUNTS = {
    "1": "0",
    "3": "0.00",
    "4": "0.00",
    "7": "0",
    "10": "0.00",
    "15": "0",
    "16": "0",
}
GIVEN_1078_48_AMOUNTS = {"13": "1.00", "14": "1.00", "15": "1.00", "45000": "0"}
GIVEN_1148_AMOUNTS = {
    "4": "1148.00",
    "10": "1077.48",
    "13": "70.52",
    "14": "70.52",
    "15": "70.52",
    "45000": "70.52",
    "16": "1077.48",
}


@pytest.mark.parametrize(
    ("salary", "expected_amounts", "expected_counts"),
    [
        ("70000", SALARY_70K_AMOUNTS, {"1": 1, "15": 0}),
        ("30000", SALARY_30K_AMOUNTS, {"15": 0}),
        ("2010", SALARY_2010_AMOUNTS, {"1": 1, "15": 1}),
        ("2032", SALARY_2032_AMOUNTS, {"15": 1}),
        ("2033", SALARY_2033_AMOUNTS, {"15": 0}),
        ("1000", SALARY_1000_AMOUNTS, {"1": 0}),
    ],
)
def test_every_line_matches_the_printed_form(
    take_home_service: TakeHomeService,
    salary: str,
    expected_amounts: dict[str, str],
    expected_counts: dict[str, int],
) -> None:
    sheet = salary_only(take_home_service, salary)

    assert amounts(sheet, expected_amounts) == {
        line: D(value) for line, value in expected_amounts.items()
    }
    assert counts(sheet, expected_counts) == expected_counts


def test_a_given_line_4_figure_is_the_premiums_deducted_and_the_overpayment_follows(
    take_home_service: TakeHomeService,
) -> None:
    sheet = compose(
        take_home_service,
        Artifact(EMPLOYMENT_INCOME, D("70000")),
        Artifact(T2204_PREMIUMS_DEDUCTED_GIVEN, D("1148.00")),
    )

    assert amounts(sheet, GIVEN_1148_AMOUNTS) == {
        line: D(value) for line, value in GIVEN_1148_AMOUNTS.items()
    }
    assert counts(sheet, {"15": 1}) == {"15": 1}


def test_an_overpayment_of_exactly_1_00_is_not_more_than_1_and_is_not_claimed(
    take_home_service: TakeHomeService,
) -> None:
    # Line 15 says "more than $1": exactly $1.00 stays off line 45000.
    sheet = compose(
        take_home_service,
        Artifact(EMPLOYMENT_INCOME, D("70000")),
        Artifact(T2204_PREMIUMS_DEDUCTED_GIVEN, D("1078.48")),
    )

    assert amounts(sheet, GIVEN_1078_48_AMOUNTS) == {
        line: D(value) for line, value in GIVEN_1078_48_AMOUNTS.items()
    }
    assert counts(sheet, {"15": 0}) == {"15": 0}


def test_the_exports_read_the_calculator_and_return_lines_at_70000(
    take_home_service: TakeHomeService,
) -> None:
    # The exports the form declares: line 4, the T1 line 45000 amount and line 16.
    sheet = salary_only(take_home_service, "70000")

    assert sheet.get(T2204_PREMIUMS_DEDUCTED).value == D("1077.48")
    assert sheet.get(EI_OVERPAYMENT).value == D("0")
    assert sheet.get(T2204_LINE_16).value == D("1077.48")


@pytest.mark.parametrize("salary", ["70000", "30000", "12345.67"])
def test_the_cent_lines_have_exactly_two_decimals(
    take_home_service: TakeHomeService, salary: str
) -> None:
    sheet = salary_only(take_home_service, salary)

    for line in CENT_LINES:
        assert sheet.get(AMOUNT_LINES[line]).value.as_tuple().exponent == -2, line


def test_line_4_at_12345_67_is_202_47(take_home_service: TakeHomeService) -> None:
    sheet = salary_only(take_home_service, "12345.67")

    assert sheet.get(T2204_PREMIUMS_DEDUCTED).value == D("202.47")


def test_a_negative_salary_is_refused(take_home_service: TakeHomeService) -> None:
    with pytest.raises(NegativeArtifactError, match="ca/employment_income cannot be negative"):
        salary_only(take_home_service, "-1")


@pytest.mark.parametrize(
    ("salary", "line_1", "line_1_plus_2"),
    [("70000", "70000.00", "70000.00"), ("20000", "20000.00", "20000.00")],
)
def test_the_cent_figures_print_cents_at_70000_and_20000(
    take_home_service: TakeHomeService, salary: str, line_1: str, line_1_plus_2: str
) -> None:
    # Line 1 (times count), line 3's sum (core/sum) and the EI overpayment (times count, a count of
    # 0 at salary only) each take the cent rule of their rounding dataset.
    sheet = salary_only(take_home_service, salary)

    for artifact, printed in (
        (T2204_LINE_1, line_1),
        (T2204_LINE_1_PLUS_2, line_1_plus_2),
        (EI_OVERPAYMENT, "0.00"),
    ):
        value = sheet.get(artifact).value
        assert str(value) == printed
        assert value.as_tuple().exponent == -2


def test_70k_trace_labels_line_16_by_its_figure(take_home_service: TakeHomeService) -> None:
    sheet = salary_only(take_home_service, "70000")

    line_16 = [line for line in sheet.trace if line.label == "t2204_line_16"]

    assert [line.amount for line in line_16] == [D("1077.48")]
    assert all(line.label is not None for line in sheet.trace)
