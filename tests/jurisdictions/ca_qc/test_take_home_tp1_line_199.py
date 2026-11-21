"""Revenu Quebec TP-1 (2025) line 199, "Add lines 101 and 105 through 164. Total income", as the
Quebec take-home manifest part wires it: line 101, the salary, plus the income of lines 105 to
164.

Each printed income line from 105 to 164 is its own optional input of the TP-1 income form, read as
0 when the caller leaves it out. The sum is `core/sum`, rounded half-up to the cent by
`ca-qc/cent_rounding`.
"""

from __future__ import annotations

from decimal import Decimal
from textwrap import dedent

import pytest

from tax_engine.adapters.inbound.trace_english import EnglishTraceRenderer
from tax_engine.domain.artifact import Artifact
from tax_engine.domain.jurisdiction_code import JurisdictionCode
from tax_engine.domain.worksheet import Worksheet
from tax_engine.jurisdictions.ca.catalog.income import EMPLOYMENT_INCOME
from tax_engine.jurisdictions.ca_qc.catalog import (
    TP1_LINE_105,
    TP1_LINE_107,
    TP1_LINE_110,
    TP1_LINE_111,
    TP1_LINE_114,
    TP1_LINE_119,
    TP1_LINE_122,
    TP1_LINE_123,
    TP1_LINE_128,
    TP1_LINE_130,
    TP1_LINE_136,
    TP1_LINE_139,
    TP1_LINE_142,
    TP1_LINE_147,
    TP1_LINE_148,
    TP1_LINE_154,
    TP1_LINE_164,
    TP1_TOTAL_INCOME_LINE_199,
)
from tests.jurisdictions.ca_qc.conftest import TakeHomeService

D = Decimal

PARTS = (
    "salary.yaml",
    "tp1_income_line_105_input.yaml",
    "tp1_income_line_107_input.yaml",
    "tp1_income_line_110_input.yaml",
    "tp1_income_line_111_input.yaml",
    "tp1_income_line_114_input.yaml",
    "tp1_income_line_119_input.yaml",
    "tp1_income_line_122_input.yaml",
    "tp1_income_line_123_input.yaml",
    "tp1_income_line_128_input.yaml",
    "tp1_income_line_130_input.yaml",
    "tp1_income_line_136_input.yaml",
    "tp1_income_line_139_input.yaml",
    "tp1_income_line_142_input.yaml",
    "tp1_income_line_147_input.yaml",
    "tp1_income_line_148_input.yaml",
    "tp1_income_line_154_input.yaml",
    "tp1_income_line_164_input.yaml",
    "tp1_income_line_199.yaml",
)

HEADER = dedent("""\
    jurisdiction: CA-QC
    version: 1
    valid_from_tax_year: 2025
    outputs:
      - ca/employment_income
    """)
FORM = dedent("""\
    form:
      name: ca-qc/tp1_income
      required: true
      exports:
        - ca-qc/tp1_total_income_line_199
    """)


LINES = (
    "105", "107", "110", "111", "114", "119", "122", "123", "128", "130",
    "136", "139", "142", "147", "148", "154", "164",
)  # fmt: skip

KINDS = {
    "105": TP1_LINE_105,
    "107": TP1_LINE_107,
    "110": TP1_LINE_110,
    "111": TP1_LINE_111,
    "114": TP1_LINE_114,
    "119": TP1_LINE_119,
    "122": TP1_LINE_122,
    "123": TP1_LINE_123,
    "128": TP1_LINE_128,
    "130": TP1_LINE_130,
    "136": TP1_LINE_136,
    "139": TP1_LINE_139,
    "142": TP1_LINE_142,
    "147": TP1_LINE_147,
    "148": TP1_LINE_148,
    "154": TP1_LINE_154,
    "164": TP1_LINE_164,
}


def tp1(take_home_service: TakeHomeService, salary: str, **lines: str) -> Worksheet:
    """The TP-1 income worksheet for a salary; a line from 105 to 164 is left out unless given."""
    starting = [Artifact(EMPLOYMENT_INCOME, D(salary))]
    for line, amount in lines.items():
        starting.append(Artifact(KINDS[line], D(amount)))
    (sheet,) = take_home_service(HEADER, FORM, *PARTS).compute(
        JurisdictionCode("CA-QC"), 2025, *starting
    )["ca-qc/tp1_income"]
    return sheet


@pytest.mark.parametrize(
    ("salary", "expected"),
    [("20000", "20000.00"), ("70000", "70000.00"), ("200000", "200000.00"), ("0", "0.00")],
)
def test_a_salary_only_total_income_is_the_salary(
    take_home_service: TakeHomeService, salary: str, expected: str
) -> None:
    value = tp1(take_home_service, salary).get(TP1_TOTAL_INCOME_LINE_199).value

    assert str(value) == expected


@pytest.mark.parametrize("line", LINES)
def test_each_line_from_105_to_164_is_added_to_the_salary(
    take_home_service: TakeHomeService, line: str
) -> None:
    value = (
        tp1(take_home_service, "70000", **{line: "1234.56"}).get(TP1_TOTAL_INCOME_LINE_199).value
    )

    assert str(value) == "71234.56"


def test_all_the_lines_are_added_together(take_home_service: TakeHomeService) -> None:
    amounts = {line: str(index * 100) for index, line in enumerate(LINES, start=1)}

    value = tp1(take_home_service, "70000", **amounts).get(TP1_TOTAL_INCOME_LINE_199).value

    assert value == D(70000 + 100 * sum(range(1, len(LINES) + 1)))


@pytest.mark.parametrize("line", ["136", "164"])
def test_a_rental_or_business_loss_is_subtracted(
    take_home_service: TakeHomeService, line: str
) -> None:
    value = tp1(take_home_service, "70000", **{line: "-500"}).get(TP1_TOTAL_INCOME_LINE_199).value

    assert value == D("69500")


def test_the_sum_is_rounded_half_up_to_the_cent(take_home_service: TakeHomeService) -> None:
    value = tp1(take_home_service, "70000", **{"154": "0.005"}).get(TP1_TOTAL_INCOME_LINE_199).value

    assert str(value) == "70000.01"


def test_the_sentence_words_the_long_sum_as_the_salary_plus_lines_105_to_164(
    take_home_service: TakeHomeService,
) -> None:
    sheet = tp1(take_home_service, "70000", **{"107": "1000", "136": "-200.50", "164": "5000"})

    sentences = EnglishTraceRenderer().render_all(sheet.trace, sheet)

    assert (
        "Line 10100 (CA$70000.00) plus lines 105 to 164 (CA$5799.50 in total) gives CA$75799.50 "
        "(rounded to the nearest cent)."
    ) in sentences
