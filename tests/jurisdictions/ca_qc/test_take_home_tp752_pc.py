"""Revenu Quebec TP-752.PC-V (2025-10 and 2026-10), "Tax Credit for Career Extension", lines 10 to
50, as the Quebec take-home manifest wires them, one step per printed line (the form is its own
form, `ca-qc/tp752_pc`, so that TP-1 line 391 can read its line 50).

Form text (confirmed, 2026-10 edition): "Eligible work income (see the information on page 2) 10";
"Subtract line 11 from line 10. If the result is $7,655 or less, you are not entitled to the tax
credit. = 12"; "Subtract line 13 from line 12. = 14"; "- 15 7,655 00"; "Subtract $7,655 from line 14
(maximum $12,755). = 16"; "x 14% Multiply line 16 by 14%. = 35"; "Net income (line 275 of your
return; see the information on page 2) 36"; "- 37 57,660 00"; "Subtract $57,660 from line 36. If the
result is negative, enter 0. = 38"; "x 7% Multiply line 38 by 7%. = 39"; "Subtract line 39 from line
35. If the result is negative, enter 0. = 40"; "Income tax on taxable income (line 401 of your
return) 47"; "Add lines 359 through 367 of your return. x 14% - 48"; "Subtract line 48 from line 47.
If the result is negative, enter 0. = 49"; "Enter the amount from line 40 or line 49, whichever is
less. Carry this amount to line 391 of your return. Tax credit for career extension 50". The 2025-10
edition prints 7,500 / $12,500 / 56,500. The expected figures are computed in `tp752_pc_support.py`
from the printed lines (not a Revenu Quebec example).

Eligibility ("65 or over on December 31") is the `ca-qc/t1_birth_year.age_65_or_older` flag, applied
as Schedule B line 22 does: line 10 is the work income times the flag, so a filer born in 1962 or
later (2026), in 1961 or later (2025) or with no birth year has 0.00 on lines 10 to 14, no credit.
The "not entitled" test of line 12 is not a step: line 14 at or below 7,655 gives a line 16 at or
below 0, so line 40 and line 50 are 0.
"""

from __future__ import annotations

from decimal import Decimal
from typing import Any

import pytest
import yaml

from tax_engine.domain.artifact import Artifact
from tax_engine.domain.kinds import AmountKind
from tax_engine.jurisdictions.ca_qc.catalog import (
    TP1_AGE_LIVING_ALONE_RETIREMENT_AMOUNT_LINE_361,
    TP1_LINE_359,
    TP1_NET_INCOME_LINE_275,
    TP752_PC_LINE_10,
    TP752_PC_LINE_11,
    TP752_PC_LINE_12,
    TP752_PC_LINE_13,
    TP752_PC_LINE_14,
    TP752_PC_LINE_15,
    TP752_PC_LINE_16,
    TP752_PC_LINE_35,
    TP752_PC_LINE_36,
    TP752_PC_LINE_37,
    TP752_PC_LINE_38,
    TP752_PC_LINE_39,
    TP752_PC_LINE_40,
    TP752_PC_LINE_47,
    TP752_PC_LINE_48,
    TP752_PC_LINE_49,
    TP752_PC_LINE_50,
    WORK_CHART_201_TOTAL_LINE_6,
    WORK_CHART_401_INCOME_TAX_LINE_8,
)
from tests.jurisdictions.ca_qc.conftest import QUEBEC_PARTS, TakeHomeService
from tests.jurisdictions.ca_qc.support import quebec_kinds
from tests.jurisdictions.ca_qc.tp752_pc_support import (
    FORM,
    Reads,
    compute,
    printed_form,
)
from tests.kinds import non_negative

D = Decimal
KINDS = {
    10: TP752_PC_LINE_10,
    11: TP752_PC_LINE_11,
    12: TP752_PC_LINE_12,
    13: TP752_PC_LINE_13,
    14: TP752_PC_LINE_14,
    15: TP752_PC_LINE_15,
    16: TP752_PC_LINE_16,
    35: TP752_PC_LINE_35,
    36: TP752_PC_LINE_36,
    37: TP752_PC_LINE_37,
    38: TP752_PC_LINE_38,
    39: TP752_PC_LINE_39,
    40: TP752_PC_LINE_40,
    47: TP752_PC_LINE_47,
    48: TP752_PC_LINE_48,
    49: TP752_PC_LINE_49,
    50: TP752_PC_LINE_50,
}
PRINTED_LINES = (10, 12, 14, 15, 16, 35, 36, 37, 38, 39, 40, 47, 48, 49, 50)


def lines_of(
    take_home_service: TakeHomeService,
    salary: str,
    year: int,
    born: int | None,
    *given: Artifact[Any],
) -> tuple[dict[int, Decimal], dict[int, Decimal]]:
    """The engine's printed lines of the form, and the lines worked out from the printed text over
    the figures of the other forms the form reads (read from their own worksheets)."""
    sheets = compute(take_home_service, salary, year=year, born=born, given=given)
    reads = Reads(
        work_income=D(salary),
        net_income=sheets["ca-qc/tp1_net_income"].get(TP1_NET_INCOME_LINE_275).value,
        income_tax=sheets["ca-qc/work_chart_401"].get(WORK_CHART_401_INCOME_TAX_LINE_8).value,
        line_359=sheets["ca-qc/tp1_credits_lines_350_to_361"].get(TP1_LINE_359).value,
        line_361=sheets["ca-qc/tp1_credits_lines_350_to_361"]
        .get(TP1_AGE_LIVING_ALONE_RETIREMENT_AMOUNT_LINE_361)
        .value,
    )
    # Work Chart 201 line 6 is the salary when nothing else is given (the export line 10 reads).
    assert sheets["ca-qc/work_chart_201"].get(WORK_CHART_201_TOTAL_LINE_6).value == D(salary)
    values = _given_lines(given)
    expected = printed_form(
        year, reads, born=born, line_11=values.get(11, D(0)), line_13=values.get(13, D(0))
    )
    sheet = sheets[FORM]
    actual = {line: sheet.get(KINDS[line]).value for line in PRINTED_LINES}
    return actual, {line: expected[line] for line in PRINTED_LINES}


def _given_lines(given: tuple[Artifact[Any], ...]) -> dict[int, Decimal]:
    return {
        line: artifact.value
        for artifact in given
        for line, kind in KINDS.items()
        if artifact.kind is kind
    }


@pytest.mark.parametrize("year", [2025, 2026])
@pytest.mark.parametrize("salary", ["7500", "7501", "7655", "7656", "12000", "20000", "70000"])
def test_every_printed_line_of_a_filer_born_in_1955_is_the_printed_arithmetic(
    take_home_service: TakeHomeService, year: int, salary: str
) -> None:
    actual, expected = lines_of(take_home_service, salary, year, 1955)

    assert actual == expected


@pytest.mark.parametrize(
    ("year", "line_15", "maximum", "line_35", "line_37"),
    [
        (2026, "7655.00", "12755.00", "1785.70", "57660.00"),
        (2025, "7500.00", "12500.00", "1750.00", "56500.00"),
    ],
)
def test_the_take_home_at_70000_born_1955_has_the_printed_figures_on_lines_10_to_37(
    take_home_service: TakeHomeService,
    year: int,
    line_15: str,
    maximum: str,
    line_35: str,
    line_37: str,
) -> None:
    # Line 14 less line 15 is 62,345.00 (2026) or 62,500.00 (2025): over the maximum, so line 16 is
    # the printed 12,755 or 12,500, and line 35 is 14% of it.
    actual, _ = lines_of(take_home_service, "70000", year, 1955)

    assert [str(actual[line]) for line in (10, 12, 14, 15, 16, 35, 37)] == [
        "70000.00",
        "70000.00",
        "70000.00",
        line_15,
        maximum,
        line_35,
        line_37,
    ]


@pytest.mark.parametrize(
    ("year", "salary", "line_16", "line_35"),
    [
        (2026, "7655", "0.00", "0.00"),
        (2026, "7656", "1.00", "0.14"),
        (2025, "7500", "0.00", "0.00"),
        (2025, "7501", "1.00", "0.14"),
    ],
)
def test_the_line_12_boundary_the_credit_starts_one_dollar_above_the_printed_figure(
    take_home_service: TakeHomeService, year: int, salary: str, line_16: str, line_35: str
) -> None:
    actual, _ = lines_of(take_home_service, salary, year, 1955)

    assert (str(actual[16]), str(actual[35])) == (line_16, line_35)


def test_line_16_and_line_35_are_0_below_line_15_and_line_40_is_0(
    take_home_service: TakeHomeService,
) -> None:
    actual, expected = lines_of(take_home_service, "5000", 2026, 1955)

    assert str(actual[16]) == "0.00"
    assert str(actual[35]) == "0.00"
    assert (actual[40], actual[50]) == (D("0.00"), D("0.00"))
    assert actual == expected


@pytest.mark.parametrize(("year", "born"), [(2026, 1961), (2025, 1960)])
def test_the_last_birth_year_of_the_age_65_flag_is_eligible(
    take_home_service: TakeHomeService, year: int, born: int
) -> None:
    actual, expected = lines_of(take_home_service, "70000", year, born)

    assert actual[10] == D("70000.00")
    assert actual[50] > 0
    assert actual == expected


@pytest.mark.parametrize(("year", "born"), [(2026, 1962), (2025, 1961), (2026, None), (2025, None)])
def test_a_younger_filer_or_a_blank_birth_year_has_no_work_income_and_no_credit(
    take_home_service: TakeHomeService, year: int, born: int | None
) -> None:
    actual, expected = lines_of(take_home_service, "70000", year, born)

    assert [actual[line] for line in (10, 12, 14, 40, 50)] == [D("0.00")] * 5
    assert actual == expected


def test_lines_11_and_13_are_subtracted_before_the_maximum(
    take_home_service: TakeHomeService,
) -> None:
    given = (
        Artifact(TP752_PC_LINE_11, D("5000.50")),
        Artifact(TP752_PC_LINE_13, D("1000.25")),
    )
    actual, expected = lines_of(take_home_service, "20000", 2026, 1955, *given)

    # 20,000.00 less 5,000.50 is 14,999.50 (line 12); less 1,000.25 is 13,999.25 (line 14); less
    # 7,655.00 is 6,344.25 (line 16, under the 12,755 maximum); at 14% 888.20 (line 35, half-up).
    assert [str(actual[line]) for line in (12, 14, 16, 35)] == [
        "14999.50",
        "13999.25",
        "6344.25",
        "888.20",
    ]
    assert actual == expected


def test_a_line_11_above_line_10_leaves_line_12_signed_and_the_credit_0(
    take_home_service: TakeHomeService,
) -> None:
    given = (Artifact(TP752_PC_LINE_11, D("5000")),)
    actual, expected = lines_of(take_home_service, "3000", 2026, 1955, *given)

    assert str(actual[12]) == "-2000.00"
    assert actual[50] == D("0.00")
    assert actual == expected


@pytest.mark.parametrize("salary", ["20000", "70000"])
def test_line_50_is_the_lesser_of_line_40_and_line_49(
    take_home_service: TakeHomeService, salary: str
) -> None:
    actual, _ = lines_of(take_home_service, salary, 2026, 1955)

    assert actual[50] == min(actual[40], actual[49])


def test_line_50_is_line_49_when_the_tax_is_the_lesser(take_home_service: TakeHomeService) -> None:
    # At $12,000 the tax on taxable income is under 14% of lines 359 and 361, so line 49 is 0.
    actual, _ = lines_of(take_home_service, "12000", 2026, 1955)

    assert actual[40] > 0
    assert actual[49] == D("0.00")
    assert actual[50] == D("0.00")


def _step_without_title(step: dict[str, Any]) -> dict[str, Any]:
    return {key: value for key, value in step.items() if key != "title"}


def _part(name: str) -> dict[str, Any]:
    part = yaml.safe_load((QUEBEC_PARTS / name).read_text(encoding="utf-8"))
    assert isinstance(part, dict)
    return part


def _steps(name: str) -> list[dict[str, Any]]:
    part = _part(name)
    assert list(part) == ["form", "capabilities"]
    assert part["form"] == {"name": FORM}
    return [_step_without_title(step) for step in part["capabilities"]]


def _op(
    name: str,
    output: str,
    consumes: dict[str, Any],
    *,
    reference: str | None = None,
    params: dict[str, str] | None = None,
    blank: dict[str, Any] | None = None,
) -> dict[str, Any]:
    step: dict[str, Any] = {"name": name}
    if reference is not None:
        step["reference"] = reference
    step["unit"] = "ca/cad"
    if params is not None:
        step["params"] = params
    if consumes:
        step["consumes"] = consumes
    if blank is not None:
        step["blank"] = blank
    step["produces"] = {"output": output}
    return step


CENT = {"rounding": "ca-qc/cent_rounding"}
EXACT = {"rounding": "ca-qc/exact_rounding"}
K = "ca-qc/tp752_pc_"
LINE_10 = [
    {
        "name": "core/first_record_count",
        "consumes": {"records": "ca-qc/t1_birth_year.age_65_or_older"},
        "blank": {"records": {"ca/age_65_or_older": "pass_on"}},
        "produces": {"output": K + "age_65_or_older"},
    },
    _op(
        "core/record_total",
        K + "work_chart_201_line_6",
        {"records": "ca-qc/work_chart_201.work_chart_201_total_line_6"},
    ),
    _op(
        "core/times_count",
        K + "line_10",
        {"amount": K + "work_chart_201_line_6", "count": K + "age_65_or_older"},
        reference="10",
        params=CENT,
        blank={"count": "0"},
    ),
]
STEPS = {
    "tp752_pc_line_10.yaml": LINE_10,
    "tp752_pc_line_12.yaml": [
        _op(
            "core/subtract",
            K + "line_12",
            {"amount": K + "line_10", "less": K + "line_11"},
            reference="12",
            params=CENT,
            blank={"less": "0"},
        )
    ],
    "tp752_pc_line_14.yaml": [
        _op(
            "core/subtract",
            K + "line_14",
            {"amount": K + "line_12", "less": K + "line_13"},
            reference="14",
            params=CENT,
            blank={"less": "0"},
        )
    ],
    "tp752_pc_line_15.yaml": [
        _op(
            "core/credit_amount",
            K + "line_15",
            {},
            reference="15",
            params={"amount": K + "line_15"},
        )
    ],
    "tp752_pc_line_16.yaml": [
        _op(
            "core/subtract_not_below_zero",
            K + "line_14_less_line_15",
            {"amount": K + "line_14", "less": K + "line_15"},
            params=EXACT,
        ),
        _op(
            "core/capped_amount",
            K + "line_16",
            {"base": K + "line_14_less_line_15"},
            reference="16",
            params={"cap": K + "line_16_maximum"},
        ),
    ],
    "tp752_pc_line_35.yaml": [
        _op(
            "core/apply_rate",
            K + "line_35",
            {"base": K + "line_16"},
            reference="35",
            params={"rate": K + "line_35_rate"},
        )
    ],
    "tp752_pc_line_36.yaml": [
        _op(
            "core/record_total",
            K + "line_36",
            {"records": "ca-qc/tp1_net_income.tp1_net_income_line_275"},
            reference="36",
        )
    ],
    "tp752_pc_line_37.yaml": [
        _op(
            "core/credit_amount",
            K + "line_37",
            {},
            reference="37",
            params={"amount": K + "line_37"},
        )
    ],
    "tp752_pc_line_38.yaml": [
        _op(
            "core/subtract_not_below_zero",
            K + "line_38",
            {"amount": K + "line_36", "less": K + "line_37"},
            reference="38",
            params=CENT,
        )
    ],
    "tp752_pc_line_39.yaml": [
        _op(
            "core/apply_rate",
            K + "line_39",
            {"base": K + "line_38"},
            reference="39",
            params={"rate": K + "line_39_rate"},
        )
    ],
    "tp752_pc_line_40.yaml": [
        _op(
            "core/subtract_not_below_zero",
            K + "line_40",
            {"amount": K + "line_35", "less": K + "line_39"},
            reference="40",
            params=CENT,
        )
    ],
    "tp752_pc_line_47.yaml": [
        _op(
            "core/record_total",
            K + "line_47",
            {"records": "ca-qc/work_chart_401.work_chart_401_income_tax_line_8"},
            reference="47",
        )
    ],
    "tp752_pc_line_48.yaml": [
        _op(
            "core/record_total",
            K + "tp1_line_359",
            {"records": "ca-qc/tp1_credits_lines_350_to_361.tp1_line_359"},
        ),
        _op(
            "core/record_total",
            K + "tp1_line_361",
            {
                "records": "ca-qc/tp1_credits_lines_350_to_361"
                ".tp1_age_living_alone_retirement_amount_line_361"
            },
        ),
        _op(
            "core/sum",
            K + "lines_359_to_367",
            {"parts": [K + "tp1_line_359", K + "tp1_line_361"]},
            params=EXACT,
        ),
        _op(
            "core/apply_rate",
            K + "line_48",
            {"base": K + "lines_359_to_367"},
            reference="48",
            params={"rate": K + "line_48_rate"},
        ),
    ],
    "tp752_pc_line_49.yaml": [
        _op(
            "core/subtract_not_below_zero",
            K + "line_49",
            {"amount": K + "line_47", "less": K + "line_48"},
            reference="49",
            params=CENT,
        )
    ],
    "tp752_pc_line_50.yaml": [
        _op(
            "core/lesser_of",
            K + "line_50",
            {"amounts": [K + "line_40", K + "line_49"]},
            reference="50",
        )
    ],
}


@pytest.mark.parametrize("part", list(STEPS))
def test_each_part_is_the_printed_line_steps_with_their_reads_and_rounding(part: str) -> None:
    assert _steps(part) == STEPS[part]


def test_the_form_is_the_career_extension_form_that_exports_line_50() -> None:
    part = _part("tp752_pc.yaml")

    assert part["form"] == {
        "name": FORM,
        "title": "Tax Credit for Career Extension",
        "required": True,
        "exports": ["ca-qc/tp752_pc_line_50"],
    }
    assert part["capabilities"] == []


@pytest.mark.parametrize(("line", "part"), [("11", "line_11"), ("13", "line_13")])
def test_lines_11_and_13_are_optional_inputs_read_as_0(line: str, part: str) -> None:
    declared = _part(f"tp752_pc_{part}_input.yaml")

    assert declared["form"] == {"name": FORM}
    (declaration,) = declared["inputs"]
    assert {k: v for k, v in declaration.items() if k not in ("title", "basis")} == {
        "name": f"ca-qc/tp752_pc_line_{line}",
        "reference": line,
        "unit": "ca/cad",
        "required": False,
        "default": None,
    }
    assert non_negative(KINDS[int(line)]) is True


@pytest.mark.parametrize("line", [10, 12, 14, 15, 16, 35, 36, 37, 38, 39, 40, 47, 48, 49, 50])
def test_the_line_kinds_are_registered_amounts(line: int) -> None:
    kind = KINDS[line]

    assert quebec_kinds().kind(kind.identifier) is kind
    assert kind.identifier == f"ca-qc/tp752_pc_line_{line}"
    assert isinstance(kind, AmountKind)


@pytest.mark.parametrize("line", [12, 14])
def test_the_lines_the_form_prints_no_floor_on_are_signed(line: int) -> None:
    assert not non_negative(KINDS[line])


@pytest.mark.parametrize("line", [15, 16, 35, 37, 38, 39, 40, 49, 50])
def test_the_floored_and_printed_figure_lines_are_non_negative(line: int) -> None:
    assert non_negative(KINDS[line])
