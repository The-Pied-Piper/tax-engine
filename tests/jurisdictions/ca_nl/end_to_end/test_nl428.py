"""Form NL428 (2025, Newfoundland and Labrador tax, single filer) from the salary alone: the real
Newfoundland and Labrador manifest composed end to end.

Every NL428 line part has its own test with its neighbours typed in. This module runs the whole
chain: the registered engine (`build_tax_computation`) over the real Newfoundland and Labrador 2025
manifest, with the gross salary (`ca/employment_income`) the only input and every optional input
left blank. It asserts the Newfoundland and Labrador tax of NL428 line 105 at salaries of $20,000,
$70,000 and $200,000.

Form text (Form NL428, CRA 5001-C): line 105 "Line 94 minus line 104 (if negative, enter "0")
... Enter this amount on line 42800 of your return.".

The line 105 figures are 0.00 / 6,147.49 / 27,192.33. Each is derived apart from the engine in
`test_line_105_follows_from_the_printed_figures`, from the printed form alone: the column of lines 2
to 8 that the taxable income falls in (printed rate and constant), the credits base (line 16, the
basic personal amount $11,067, plus the CPP and EI amounts of lines 27 and 29) at the printed 8.7%,
and the low-income tax reduction of lines 95 to 104 ($997 less 16% of the adjusted family income
above $23,928). The taxable income is the salary less the CPP enhanced contribution (1% of the
salary up to $71,300 less $3,500, and 4% from $71,300 to $81,200). The figures are not a CRA
example.
"""

from __future__ import annotations

from decimal import ROUND_HALF_UP, Decimal

import pytest

from tax_engine import build_tax_computation
from tax_engine.domain.artifact import Artifact
from tax_engine.domain.jurisdiction_code import JurisdictionCode
from tax_engine.domain.kinds import AmountKind
from tax_engine.domain.worksheet import Worksheet
from tax_engine.jurisdictions.ca.catalog.income import EMPLOYMENT_INCOME
from tax_engine.registrations import artifact_kinds

D = Decimal
NEWFOUNDLAND = JurisdictionCode("CA-NL")
NL428 = "ca-nl/nl428"
NL428_CREDITS = "ca-nl/nl428_credits"
LINE_1 = "ca-nl/nl428_taxable_income_line_1"
LINE_63 = "ca-nl/nl428_newfoundland_and_labrador_tax_on_taxable_income_line_63"
LINE_62 = "ca-nl/nl428_non_refundable_credits_line_62"
LINE_87 = "ca-nl/nl428_tax_line_87"
LINE_103 = "ca-nl/nl428_line_103"
LINE_105 = "ca-nl/nl428_newfoundland_and_labrador_tax_line_105"
SALARIES = [("20000", "0.00"), ("70000", "6147.49"), ("200000", "27192.33")]


def _figure(sheet: Worksheet, name: str) -> Decimal:
    kind = artifact_kinds().kind(name)
    assert isinstance(kind, AmountKind)
    return sheet.get(kind).value


def _cents(amount: Decimal) -> Decimal:
    return amount.quantize(D("0.01"), ROUND_HALF_UP)


def _worksheets(salary: str) -> dict[str, tuple[Worksheet, ...]]:
    return build_tax_computation().compute(
        NEWFOUNDLAND, 2025, Artifact(EMPLOYMENT_INCOME, D(salary))
    )


@pytest.mark.parametrize(("salary", "newfoundland_tax"), SALARIES)
def test_line_105_is_the_newfoundland_and_labrador_tax(salary: str, newfoundland_tax: str) -> None:
    (nl428,) = _worksheets(salary)[NL428]

    assert _figure(nl428, LINE_105) == D(newfoundland_tax)


def test_line_105_at_20000_follows_from_the_printed_figures() -> None:
    worksheets = _worksheets("20000")
    (credits_sheet,) = worksheets[NL428_CREDITS]
    (nl428,) = worksheets[NL428]
    taxable_income = D("20000") - _cents((D("20000") - D("3500")) * D("0.01"))
    # Column 1 (line 1 of $44,192 or less): rate 8.7%, constant 0.00.
    tax_on_taxable_income = _cents(taxable_income * D("0.087"))
    cpp = (D("20000") - D("3500")) * D("0.0495")
    ei = _cents(D("20000") * D("0.0164"))
    credits = _cents((D("11067") + cpp + ei) * D("0.087"))
    line_87 = tax_on_taxable_income - credits
    # Lines 95 to 104: adjusted family income 19,835.00 is below the printed 23,928.
    line_104 = D("997") - _cents(max(taxable_income - D("23928"), D("0")) * D("0.16"))

    assert taxable_income == D("19835.00")
    assert (cpp, ei) == (D("816.75"), D("328.00"))
    assert tax_on_taxable_income == D("1725.65")
    assert credits == D("1062.42")
    assert line_87 == D("663.23")
    assert line_104 == D("997.00")
    assert _figure(credits_sheet, LINE_1) == taxable_income
    assert _figure(nl428, LINE_63) == tax_on_taxable_income
    assert _figure(credits_sheet, LINE_62) == credits
    assert _figure(nl428, LINE_87) == line_87
    assert max(line_87 - line_104, D("0")) == D("0.00")
    assert _figure(nl428, LINE_105) == D("0.00")


def test_line_105_at_70000_follows_from_the_printed_figures() -> None:
    worksheets = _worksheets("70000")
    (credits_sheet,) = worksheets[NL428_CREDITS]
    (nl428,) = worksheets[NL428]
    taxable_income = D("70000") - _cents((D("70000") - D("3500")) * D("0.01"))
    # Column 2 (line 1 more than $44,192 but not more than $88,382): 14.5%, constant 3,844.70.
    tax_on_taxable_income = _cents((taxable_income - D("44192")) * D("0.145") + D("3844.70"))
    cpp = (D("70000") - D("3500")) * D("0.0495")
    # The EI premium stops at the maximum insurable earnings of $65,700.
    ei = _cents(D("65700") * D("0.0164"))
    credits = _cents((D("11067") + cpp + ei) * D("0.087"))
    line_87 = tax_on_taxable_income - credits
    # Lines 99 to 104: 16% of the adjusted family income above $23,928 is above the $997 reduction.
    line_103 = _cents((taxable_income - D("23928")) * D("0.16"))

    assert taxable_income == D("69335.00")
    assert (cpp, ei) == (D("3291.75"), D("1077.48"))
    assert tax_on_taxable_income == D("7490.44")
    assert credits == D("1342.95")
    assert line_87 == D("6147.49")
    assert line_103 == D("7265.12")
    assert D("997") - line_103 < 0
    assert _figure(credits_sheet, LINE_1) == taxable_income
    assert _figure(nl428, LINE_63) == tax_on_taxable_income
    assert _figure(credits_sheet, LINE_62) == credits
    assert _figure(nl428, LINE_103) == line_103
    assert _figure(nl428, LINE_87) == line_87
    assert _figure(nl428, LINE_105) == D("6147.49")


def test_line_105_at_200000_follows_from_the_printed_figures() -> None:
    worksheets = _worksheets("200000")
    (credits_sheet,) = worksheets[NL428_CREDITS]
    (nl428,) = worksheets[NL428]
    # The CPP enhanced contribution is 1% of 71,300 less 3,500 and 4% of 81,200 less 71,300.
    enhanced = _cents(D("67800") * D("0.01")) + _cents(D("9900") * D("0.04"))
    taxable_income = D("200000") - enhanced
    # Column 4 (line 1 more than $157,792 but not more than $220,910): 17.8%, constant 21,219.03.
    tax_on_taxable_income = _cents((taxable_income - D("157792")) * D("0.178") + D("21219.03"))
    cpp = D("67800") * D("0.0495")
    ei = _cents(D("65700") * D("0.0164"))
    credits = _cents((D("11067") + cpp + ei) * D("0.087"))
    line_87 = tax_on_taxable_income - credits

    assert enhanced == D("1074.00")
    assert taxable_income == D("198926.00")
    assert cpp == D("3356.10")
    assert tax_on_taxable_income == D("28540.88")
    assert credits == D("1348.55")
    assert line_87 == D("27192.33")
    assert _figure(credits_sheet, LINE_1) == taxable_income
    assert _figure(nl428, LINE_63) == tax_on_taxable_income
    assert _figure(credits_sheet, LINE_62) == credits
    assert _figure(nl428, LINE_87) == line_87
    assert _figure(nl428, LINE_105) == D("27192.33")
