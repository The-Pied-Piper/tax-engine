"""Unit tests for reading the generic (core) parameter kinds through YamlParameterSource.

Values are made up.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from tax_engine.adapters.outbound.yaml_parameters import YamlParameterSource
from tax_engine.domain.errors import (
    InvalidAmountError,
    InvalidClassRatesError,
    InvalidConditionsError,
    InvalidCreditError,
    InvalidFactorError,
    InvalidFractionError,
    InvalidParameterDataError,
    InvalidRateError,
    InvalidRateTableError,
    InvalidSurchargeTiersError,
    InvalidThresholdRateError,
)
from tax_engine.domain.parameters.amount import AMOUNT, Amount
from tax_engine.domain.parameters.brackets import BRACKETS, Bracket, BracketSchedule
from tax_engine.domain.parameters.class_rates import (
    CLASS_RATES,
    ClassElection,
    ClassRate,
    ClassRates,
    HalfYearRule,
    HalfYearRuleOnSale,
    RecaptureAndTerminalLoss,
)
from tax_engine.domain.parameters.conditions import (
    CONDITIONS,
    Condition,
    ConditionList,
    ConditionPart,
    ConditionTest,
)
from tax_engine.domain.parameters.credit import CREDIT, Credit
from tax_engine.domain.parameters.datasets import ParameterDataset
from tax_engine.domain.parameters.factor import FACTOR, Factor
from tax_engine.domain.parameters.fraction import FRACTION, Fraction
from tax_engine.domain.parameters.rate import RATE, Rate
from tax_engine.domain.parameters.rate_table import RATE_TABLE, RateTable, RateTableRow
from tax_engine.domain.parameters.rounding import NO_ROUNDING, RoundingMode, RoundTo
from tax_engine.domain.parameters.rounding_only import ROUNDING_ONLY, RoundingOnly
from tax_engine.domain.parameters.surcharge_tiers import (
    SURCHARGE_TIERS,
    SurchargeTier,
    SurchargeTiers,
)
from tax_engine.domain.parameters.threshold_rate import THRESHOLD_RATE, ThresholdRate
from tests.parameter_source_support import (
    AMOUNT_2025,
    BRACKETS_2025,
    CREDIT_2025,
    RATE_2025,
    D,
    roots,
    write,
)
from tests.parameter_source_support import (
    core_parsers as built_in_parsers,
)


def source(directory: Path) -> YamlParameterSource:
    return YamlParameterSource(roots(directory), parsers=built_in_parsers())


THRESHOLD_RATE_2025 = """\
family: ex/threshold_rate
tax_year: 2025
kind: threshold_rate
sources:
  - https://example.org/threshold-rate-2025
rounding: none
threshold: "52886"
rate: "0.0505"
"""


SURCHARGE_TIERS_2025 = """\
family: ex/surcharge_tiers
tax_year: 2025
kind: surcharge_tiers
sources:
  - https://example.org/surcharge-2025
rounding: none
tiers:
  - {threshold: "100", rate: "0.10"}
  - {threshold: "300.50", rate: "0.25"}
"""


CAPPED_SURCHARGE_TIERS_2025 = """\
family: ex/surcharge_tiers
tax_year: 2025
kind: surcharge_tiers
sources:
  - https://example.org/surcharge-2025
rounding: none
tiers:
  - {threshold: "100", rate: "0.10"}
  - {threshold: "300.50", rate: "0.25", maximum: "150.50"}
"""


FACTOR_2025 = """\
family: ex/factor
tax_year: 2025
kind: factor
sources:
  - https://example.org/factor-2025
rounding: none
value: "2"
"""


FRACTION_2025 = """\
family: ex/fraction
tax_year: 2025
kind: fraction
sources:
  - https://example.org/fraction-2025
rounding: none
numerator: "2"
denominator: "3"
"""


RATE_TABLE_2025 = """\
family: ex/rate_table
tax_year: 2025
kind: rate_table
sources:
  - https://example.org/rate-table-2025
rounding: none
rate_at_zero: "0.30"
rows:
  - {more_than: "0", not_more_than: "1000", rate: "0.30"}
  - {more_than: "1000", not_more_than: "2500.50", rate: "0.20"}
  - {more_than: "2500.50", rate: "0"}
"""


CLASS_RATES_2025 = """\
family: ex/class_rates
tax_year: 2025
kind: class_rates
sources:
  - https://example.org/class-rates-2025
rounding: none
full_year_days: "365"
longest_fiscal_period_days: "366"
classes:
  "8":
    rate: "0.20"
    half_year_rule: applies
    recapture_and_terminal_loss: applies
    half_year_rule_on_sale: does_not_apply
    aiip_factor: {numerator: "0", denominator: "1"}
    riip_factor: {numerator: "1", denominator: "2"}
  "10.1":
    rate: "0.30"
    half_year_rule: applies
    recapture_and_terminal_loss: excluded
    half_year_rule_on_sale: applies
    aiip_factor: {numerator: "0", denominator: "1"}
    riip_factor: {numerator: "1", denominator: "2"}
  "43.1":
    rate: "0.30"
    half_year_rule: applies
    recapture_and_terminal_loss: applies
    half_year_rule_on_sale: does_not_apply
    aiip_factor: {numerator: "3", denominator: "2"}
    riip_factor: {numerator: "7", denominator: "3"}
  "12":
    rate: "1"
    half_year_rule: exempt
    recapture_and_terminal_loss: applies
    half_year_rule_on_sale: does_not_apply
    aiip_factor: {numerator: "0", denominator: "1"}
    riip_factor: {numerator: "0", denominator: "1"}
"""


CONDITIONS_2025 = """\
family: ex/conditions
tax_year: 2025
kind: conditions
sources:
  - https://example.org/conditions-2025
rounding: none
count_when_any_applies: "0"
conditions:
  - text: You were bankrupt at any time in 2025
    parts:
      - tests:
          - {reads: count, position: "1", relation: equal_to, than: "1"}
  - text: There is an amount on line 72
    parts:
      - tests:
          - {reads: amount, position: "1", relation: not_equal_to, than: "0"}
  - text: You entered an amount and the other amount is more than $82,125.50
    parts:
      - tests:
          - {reads: count, position: "2", relation: not_equal_to, than: "0"}
          - {reads: amount, position: "2", relation: not_equal_to, than: "0"}
      - tests:
          - {reads: amount, position: "3", relation: more_than, than: "82125.50"}
  - text: The first amount is more than the second
    parts:
      - tests:
          - {reads: amount, position: "1", relation: more_than, against: "2"}
"""


ROUNDING_ONLY_2025 = """\
family: ex/rounding_only
tax_year: 2025
kind: rounding_only
sources:
  - https://example.org/rounding-only-2025
rounding: {increment: "0.01", mode: half_up}
"""


def test_reads_a_bracket_dataset(tmp_path: Path) -> None:
    write(tmp_path, "ex/parameters/brackets/2025.yaml", BRACKETS_2025)

    result = source(tmp_path).get("ex/brackets", 2025, BRACKETS)

    assert result == ParameterDataset(
        family="ex/brackets",
        tax_year=2025,
        kind=BRACKETS,
        values=BracketSchedule((Bracket(D("0"), D("0.10")), Bracket(D("100"), D("0.20")))),
        rounding=NO_ROUNDING,
        sources=("https://example.org/rates-2025",),
    )


def test_reads_a_credit_dataset(tmp_path: Path) -> None:
    write(tmp_path, "ex/parameters/personal_credit/2025.yaml", CREDIT_2025)

    result = source(tmp_path).get("ex/personal_credit", 2025, CREDIT)

    assert result == ParameterDataset(
        family="ex/personal_credit",
        tax_year=2025,
        kind=CREDIT,
        values=Credit(amount=D("1000")),
        rounding=NO_ROUNDING,
        sources=("https://example.org/credits-2025",),
    )


def test_reads_a_rate_dataset(tmp_path: Path) -> None:
    write(tmp_path, "ex/parameters/credit_rate/2025.yaml", RATE_2025)

    result = source(tmp_path).get("ex/credit_rate", 2025, RATE)

    assert result == ParameterDataset(
        family="ex/credit_rate",
        tax_year=2025,
        kind=RATE,
        values=Rate(D("0.125")),
        rounding=NO_ROUNDING,
        sources=("https://example.org/credit-rate-2025",),
    )


@pytest.mark.parametrize("rate", ["0", "1", "0.0505"])
def test_reads_rates_from_zero_to_one_inclusive(tmp_path: Path, rate: str) -> None:
    write(
        tmp_path,
        "ex/parameters/credit_rate/2025.yaml",
        RATE_2025.replace('rate: "0.125"', f'rate: "{rate}"'),
    )

    assert source(tmp_path).get("ex/credit_rate", 2025, RATE).values == Rate(D(rate))


def test_reads_an_amount_dataset(tmp_path: Path) -> None:
    write(tmp_path, "ex/parameters/amount_cap/2025.yaml", AMOUNT_2025)

    result = source(tmp_path).get("ex/amount_cap", 2025, AMOUNT)

    assert result == ParameterDataset(
        family="ex/amount_cap",
        tax_year=2025,
        kind=AMOUNT,
        values=Amount(D("1471")),
        rounding=NO_ROUNDING,
        sources=("https://example.org/amount-cap-2025",),
    )


@pytest.mark.parametrize("amount", ["0", "1471", "1234.56", "1000.50"])
def test_reads_amounts_exactly(tmp_path: Path, amount: str) -> None:
    write(
        tmp_path,
        "ex/parameters/amount_cap/2025.yaml",
        AMOUNT_2025.replace('amount: "1471"', f'amount: "{amount}"'),
    )

    value = source(tmp_path).get("ex/amount_cap", 2025, AMOUNT).values.value

    assert str(value) == amount  # exact, scale kept


def test_reads_an_amount_dataset_rounding_rule(tmp_path: Path) -> None:
    write(
        tmp_path,
        "ex/parameters/amount_cap/2025.yaml",
        AMOUNT_2025.replace("rounding: none", 'rounding: {increment: "1", mode: down}'),
    )

    result = source(tmp_path).get("ex/amount_cap", 2025, AMOUNT)

    assert result.rounding == RoundTo(D("1"), RoundingMode.DOWN)


def test_by_default_the_amount_parser_comes_from_the_shared_registry(tmp_path: Path) -> None:
    write(tmp_path, "ex/parameters/amount_cap/2025.yaml", AMOUNT_2025)

    result = YamlParameterSource(roots(tmp_path), built_in_parsers()).get(
        "ex/amount_cap", 2025, AMOUNT
    )

    assert result.values == Amount(D("1471"))


def test_reads_a_surcharge_tiers_dataset(tmp_path: Path) -> None:
    write(tmp_path, "ex/parameters/surcharge_tiers/2025.yaml", SURCHARGE_TIERS_2025)

    result = source(tmp_path).get("ex/surcharge_tiers", 2025, SURCHARGE_TIERS)

    assert result == ParameterDataset(
        family="ex/surcharge_tiers",
        tax_year=2025,
        kind=SURCHARGE_TIERS,
        values=SurchargeTiers(
            (
                SurchargeTier(D("100"), Rate(D("0.10"))),
                SurchargeTier(D("300.50"), Rate(D("0.25"))),
            )
        ),
        rounding=NO_ROUNDING,
        sources=("https://example.org/surcharge-2025",),
    )


def test_reads_surcharge_tiers_exactly(tmp_path: Path) -> None:
    write(tmp_path, "ex/parameters/surcharge_tiers/2025.yaml", SURCHARGE_TIERS_2025)

    tiers = source(tmp_path).get("ex/surcharge_tiers", 2025, SURCHARGE_TIERS).values.tiers

    assert [str(tier.threshold) for tier in tiers] == ["100", "300.50"]  # exact, scale kept
    assert [str(tier.rate.value) for tier in tiers] == ["0.10", "0.25"]


def test_reads_a_single_surcharge_tier(tmp_path: Path) -> None:
    write(
        tmp_path,
        "ex/parameters/surcharge_tiers/2025.yaml",
        SURCHARGE_TIERS_2025.replace('  - {threshold: "300.50", rate: "0.25"}\n', ""),
    )

    result = source(tmp_path).get("ex/surcharge_tiers", 2025, SURCHARGE_TIERS)

    assert result.values == SurchargeTiers((SurchargeTier(D("100"), Rate(D("0.10"))),))


def test_reads_a_surcharge_tiers_rounding_rule(tmp_path: Path) -> None:
    write(
        tmp_path,
        "ex/parameters/surcharge_tiers/2025.yaml",
        SURCHARGE_TIERS_2025.replace(
            "rounding: none", 'rounding: {increment: "0.01", mode: half_up}'
        ),
    )

    result = source(tmp_path).get("ex/surcharge_tiers", 2025, SURCHARGE_TIERS)

    assert result.rounding == RoundTo(D("0.01"), RoundingMode.HALF_UP)


def test_by_default_the_surcharge_tiers_parser_comes_from_the_shared_registry(
    tmp_path: Path,
) -> None:
    write(tmp_path, "ex/parameters/surcharge_tiers/2025.yaml", SURCHARGE_TIERS_2025)

    result = YamlParameterSource(roots(tmp_path), built_in_parsers()).get(
        "ex/surcharge_tiers", 2025, SURCHARGE_TIERS
    )

    assert result.values.tiers[0] == SurchargeTier(D("100"), Rate(D("0.10")))


def test_reads_a_factor_dataset(tmp_path: Path) -> None:
    write(tmp_path, "ex/parameters/factor/2025.yaml", FACTOR_2025)

    result = source(tmp_path).get("ex/factor", 2025, FACTOR)

    assert result == ParameterDataset(
        family="ex/factor",
        tax_year=2025,
        kind=FACTOR,
        values=Factor(D("2")),
        rounding=NO_ROUNDING,
        sources=("https://example.org/factor-2025",),
    )


@pytest.mark.parametrize("value", ["0", "1", "2", "2.50", "1000000"])
def test_reads_factors_exactly(tmp_path: Path, value: str) -> None:
    write(
        tmp_path,
        "ex/parameters/factor/2025.yaml",
        FACTOR_2025.replace('value: "2"', f'value: "{value}"'),
    )

    factor = source(tmp_path).get("ex/factor", 2025, FACTOR).values.value

    assert str(factor) == value  # exact, scale kept, no upper bound


def test_reads_a_factor_datasets_rounding_rule(tmp_path: Path) -> None:
    write(
        tmp_path,
        "ex/parameters/factor/2025.yaml",
        FACTOR_2025.replace("rounding: none", 'rounding: {increment: "0.01", mode: half_up}'),
    )

    result = source(tmp_path).get("ex/factor", 2025, FACTOR)

    assert result.rounding == RoundTo(D("0.01"), RoundingMode.HALF_UP)


def test_by_default_the_factor_parser_comes_from_the_shared_registry(tmp_path: Path) -> None:
    write(tmp_path, "ex/parameters/factor/2025.yaml", FACTOR_2025)

    result = YamlParameterSource(roots(tmp_path), built_in_parsers()).get("ex/factor", 2025, FACTOR)

    assert result.values == Factor(D("2"))


def test_reads_a_fraction_dataset(tmp_path: Path) -> None:
    write(tmp_path, "ex/parameters/fraction/2025.yaml", FRACTION_2025)

    result = source(tmp_path).get("ex/fraction", 2025, FRACTION)

    assert result == ParameterDataset(
        family="ex/fraction",
        tax_year=2025,
        kind=FRACTION,
        values=Fraction(numerator=2, denominator=3),
        rounding=NO_ROUNDING,
        sources=("https://example.org/fraction-2025",),
    )


@pytest.mark.parametrize(
    ("numerator", "denominator"),
    [("1", "1"), ("2", "3"), ("3", "2"), ("4", "6"), ("7", "1000000"), ("0", "3"), ("0", "1")],
)
def test_reads_a_fractions_parts_as_whole_numbers(
    tmp_path: Path, numerator: str, denominator: str
) -> None:
    content = FRACTION_2025.replace('numerator: "2"', f'numerator: "{numerator}"').replace(
        'denominator: "3"', f'denominator: "{denominator}"'
    )
    write(tmp_path, "ex/parameters/fraction/2025.yaml", content)

    fraction = source(tmp_path).get("ex/fraction", 2025, FRACTION).values

    assert (fraction.numerator, fraction.denominator) == (int(numerator), int(denominator))
    assert type(fraction.numerator) is int
    assert type(fraction.denominator) is int


def test_reads_a_fraction_datasets_rounding_rule(tmp_path: Path) -> None:
    write(
        tmp_path,
        "ex/parameters/fraction/2025.yaml",
        FRACTION_2025.replace("rounding: none", 'rounding: {increment: "0.01", mode: half_up}'),
    )

    result = source(tmp_path).get("ex/fraction", 2025, FRACTION)

    assert result.rounding == RoundTo(D("0.01"), RoundingMode.HALF_UP)


def test_by_default_the_fraction_parser_comes_from_the_shared_registry(tmp_path: Path) -> None:
    write(tmp_path, "ex/parameters/fraction/2025.yaml", FRACTION_2025)

    result = YamlParameterSource(roots(tmp_path), built_in_parsers()).get(
        "ex/fraction", 2025, FRACTION
    )

    assert result.values == Fraction(2, 3)


# 10.5% to 105, 20.5% above: the exact tax at the second bracket's start is 11.025.
HALF_CENT_BRACKETS = BRACKETS_2025.replace('rate: "0.10"', 'rate: "0.105"').replace(
    '{from: "100", rate: "0.20"}', '{from: "105", rate: "0.205"}'
)


def test_a_bracket_dataset_without_a_tax_at_start_rounding_rule_does_not_round(
    tmp_path: Path,
) -> None:
    write(
        tmp_path,
        "ex/parameters/brackets/2025.yaml",
        HALF_CENT_BRACKETS.replace("tax_at_start_rounding: none\n", ""),
    )

    schedule = source(tmp_path).get("ex/brackets", 2025, BRACKETS).values

    assert schedule.tax_at_start_rounding == NO_ROUNDING
    assert schedule.column_for(D(150)).tax_at_start == D("11.025")


def test_reads_a_printed_tax_at_start_per_bracket_as_given(tmp_path: Path) -> None:
    write(
        tmp_path,
        "ex/parameters/brackets/2025.yaml",
        HALF_CENT_BRACKETS.replace("tax_at_start_rounding: none\n", "").replace(
            '{from: "105", rate: "0.205"}', '{from: "105", rate: "0.205", tax_at_start: "11.0250"}'
        ),
    )

    schedule = source(tmp_path).get("ex/brackets", 2025, BRACKETS).values

    assert schedule.brackets[1].tax_at_start == D("11.0250")
    assert schedule.brackets[0].tax_at_start is None
    assert schedule.column_for(D(150)).tax_at_start == D("11.0250")


def test_reads_a_tax_at_start_rounding_rule(tmp_path: Path) -> None:
    write(
        tmp_path,
        "ex/parameters/brackets/2025.yaml",
        HALF_CENT_BRACKETS.replace(
            "tax_at_start_rounding: none\n",
            'tax_at_start_rounding: {increment: "0.01", mode: half_up}\n',
        ),
    )

    schedule = source(tmp_path).get("ex/brackets", 2025, BRACKETS).values

    assert schedule == BracketSchedule(
        (Bracket(D("0"), D("0.105")), Bracket(D("105"), D("0.205"))),
        RoundTo(D("0.01"), RoundingMode.HALF_UP),
    )
    assert schedule.column_for(D(150)).tax_at_start == D("11.03")


def test_reads_a_tax_at_start_rounding_of_none_as_no_rounding(tmp_path: Path) -> None:
    write(
        tmp_path,
        "ex/parameters/brackets/2025.yaml",
        HALF_CENT_BRACKETS,
    )

    schedule = source(tmp_path).get("ex/brackets", 2025, BRACKETS).values

    assert schedule.tax_at_start_rounding == NO_ROUNDING
    assert schedule.column_for(D(150)).tax_at_start == D("11.025")


def test_reads_a_tax_at_start_rounding_rule_other_than_the_cent(tmp_path: Path) -> None:
    write(
        tmp_path,
        "ex/parameters/brackets/2025.yaml",
        HALF_CENT_BRACKETS.replace(
            "tax_at_start_rounding: none\n",
            'tax_at_start_rounding: {increment: "1", mode: down}\n',
        ),
    )

    schedule = source(tmp_path).get("ex/brackets", 2025, BRACKETS).values

    assert schedule.tax_at_start_rounding == RoundTo(D("1"), RoundingMode.DOWN)
    assert schedule.column_for(D(150)).tax_at_start == D("11")


def test_the_tax_at_start_rounding_and_the_rounding_rule_are_read_apart(tmp_path: Path) -> None:
    write(
        tmp_path,
        "ex/parameters/brackets/2025.yaml",
        HALF_CENT_BRACKETS.replace(
            "\nrounding: none\ntax_at_start_rounding: none\n",
            '\nrounding: {increment: "1", mode: down}\n'
            'tax_at_start_rounding: {increment: "0.01", mode: half_up}\n',
        ),
    )

    result = source(tmp_path).get("ex/brackets", 2025, BRACKETS)

    assert result.rounding == RoundTo(D("1"), RoundingMode.DOWN)
    assert result.values.tax_at_start_rounding == RoundTo(D("0.01"), RoundingMode.HALF_UP)


def test_the_rounding_rule_does_not_round_the_tax_at_each_start(tmp_path: Path) -> None:
    write(
        tmp_path,
        "ex/parameters/brackets/2025.yaml",
        HALF_CENT_BRACKETS.replace(
            "\nrounding: none", '\nrounding: {increment: "0.01", mode: half_up}'
        ),
    )

    schedule = source(tmp_path).get("ex/brackets", 2025, BRACKETS).values

    assert schedule.tax_at_start_rounding == NO_ROUNDING
    assert schedule.column_for(D(150)).tax_at_start == D("11.025")


def test_a_tax_at_start_rounding_rule_belongs_to_brackets_datasets_only(tmp_path: Path) -> None:
    write(
        tmp_path,
        "ex/parameters/rate/2025.yaml",
        RATE_2025 + "tax_at_start_rounding: none\n",
    )

    with pytest.raises(
        InvalidParameterDataError, match=r"unknown keys \['tax_at_start_rounding'\]"
    ):
        source(tmp_path).get("ex/rate", 2025, RATE)


def test_reads_a_rounding_rule(tmp_path: Path) -> None:
    write(
        tmp_path,
        "ex/parameters/brackets/2025.yaml",
        BRACKETS_2025.replace("\nrounding: none", '\nrounding: {increment: "0.01", mode: half_up}'),
    )

    result = source(tmp_path).get("ex/brackets", 2025, BRACKETS)

    assert result.rounding == RoundTo(D("0.01"), RoundingMode.HALF_UP)


@pytest.mark.parametrize(
    ("content", "message"),
    [
        pytest.param(
            BRACKETS_2025.replace("kind: brackets", "kind: credit"),
            "kind 'credit' does not match the requested 'brackets'",
            id="kind-mismatch",
        ),
        pytest.param(
            BRACKETS_2025.replace("kind: brackets\n", ""), "missing key 'kind'", id="kind-missing"
        ),
        pytest.param(
            BRACKETS_2025.replace("family: ex/brackets", "family: ex/other"),
            "family 'ex/other' does not match",
            id="family-mismatch",
        ),
        pytest.param(
            BRACKETS_2025.replace("tax_year: 2025", "tax_year: 2024"),
            "tax_year 2024 does not match",
            id="year-mismatch",
        ),
        pytest.param(BRACKETS_2025 + "extra: 1\n", r"unknown keys \['extra'\]", id="unknown-key"),
        pytest.param(
            BRACKETS_2025 + "amount: '1'\n",
            r"unknown keys \['amount'\]",
            id="other-kinds-key",
        ),
        pytest.param(
            BRACKETS_2025.replace("\nrounding: none\n", "\n"),
            r"missing keys \['rounding'\]",
            id="rounding-missing",
        ),
        pytest.param(
            BRACKETS_2025 + "tax_year: 2025\n", "duplicate key 'tax_year'", id="duplicate-key"
        ),
        pytest.param(
            BRACKETS_2025.replace('rate: "0.10"', "rate: 0.10"),
            r"brackets\[0\].rate must be a string, got float",
            id="rate-as-yaml-number",
        ),
        pytest.param(
            BRACKETS_2025.replace('rate: "0.10"', 'rate: "ten"'),
            r"brackets\[0\].rate is not a decimal: 'ten'",
            id="rate-not-decimal",
        ),
        pytest.param(
            BRACKETS_2025.replace('{from: "100"', '{from: "0"'),
            "strictly ascending",
            id="schedule-invalid",
        ),
        pytest.param(
            BRACKETS_2025.replace('rate: "0.20"}', 'rate: "0.20", tax_at_start: 10}'),
            r"brackets\[1\].tax_at_start must be a string, got int",
            id="tax-at-start-as-yaml-number",
        ),
        pytest.param(
            BRACKETS_2025.replace('rate: "0.20"}', 'rate: "0.20", tax_at_start: "ten"}'),
            r"brackets\[1\].tax_at_start is not a decimal: 'ten'",
            id="tax-at-start-not-decimal",
        ),
        pytest.param(
            BRACKETS_2025.replace('rate: "0.20"}', 'rate: "0.20", tax_at_start: "-1"}'),
            "tax_at_start must not be negative",
            id="tax-at-start-negative",
        ),
        pytest.param(
            BRACKETS_2025.replace('rate: "0.20"}', 'rate: "0.20", tax_at_start: "NaN"}'),
            "tax_at_start is not a decimal",
            id="tax-at-start-not-finite",
        ),
        pytest.param(
            BRACKETS_2025.replace('rate: "0.20"}', 'rate: "0.20", to: "300"}'),
            r"brackets\[1\]: unknown keys \['to'\]",
            id="no-upper-bound-key",
        ),
        pytest.param(
            BRACKETS_2025.replace('{from: "100", rate: "0.20"}', '{from: "100"}'),
            r"brackets\[1\]: missing keys \['rate'\]",
            id="rate-missing",
        ),
        pytest.param(
            BRACKETS_2025.replace(
                "tax_at_start_rounding: none\n", "tax_at_start_rounding: always\n"
            ),
            "tax_at_start_rounding must be 'none' or a mapping of increment and mode",
            id="tax-at-start-rounding-unknown-word",
        ),
        pytest.param(
            BRACKETS_2025.replace("tax_at_start_rounding: none\n", "tax_at_start_rounding: null\n"),
            "tax_at_start_rounding must be 'none' or a mapping of increment and mode",
            id="tax-at-start-rounding-null",
        ),
        pytest.param(
            BRACKETS_2025.replace(
                "tax_at_start_rounding: none\n",
                'tax_at_start_rounding: {increment: "0.01", mode: sideways}\n',
            ),
            "tax_at_start_rounding.mode 'sideways' is not one of",
            id="tax-at-start-rounding-unknown-mode",
        ),
        pytest.param(
            BRACKETS_2025.replace(
                "tax_at_start_rounding: none\n",
                'tax_at_start_rounding: {increment: "0", mode: down}\n',
            ),
            "increment must be a positive",
            id="tax-at-start-rounding-zero-increment",
        ),
        pytest.param(
            BRACKETS_2025.replace(
                "tax_at_start_rounding: none\n", 'tax_at_start_rounding: {increment: "0.01"}\n'
            ),
            r"tax_at_start_rounding: missing keys \['mode'\]",
            id="tax-at-start-rounding-mode-missing",
        ),
        pytest.param(
            BRACKETS_2025.replace(
                "tax_at_start_rounding: none\n",
                'tax_at_start_rounding: {increment: "1", mode: up, step: "1"}\n',
            ),
            r"tax_at_start_rounding: unknown keys \['step'\]",
            id="tax-at-start-rounding-unknown-key",
        ),
        pytest.param(
            BRACKETS_2025.replace(
                "tax_at_start_rounding: none\n",
                "tax_at_start_rounding: {increment: 0.01, mode: down}\n",
            ),
            "tax_at_start_rounding.increment must be a string, got float",
            id="tax-at-start-rounding-increment-as-yaml-number",
        ),
        pytest.param(
            BRACKETS_2025 + "tax_at_start_rounding: none\n",
            "duplicate key 'tax_at_start_rounding'",
            id="tax-at-start-rounding-duplicate",
        ),
        pytest.param(
            BRACKETS_2025.replace("\nrounding: none", "\nrounding: always"),
            "rounding must be 'none' or a mapping",
            id="rounding-unknown-word",
        ),
        pytest.param(
            BRACKETS_2025.replace(
                "\nrounding: none", '\nrounding: {increment: "0.01", mode: sideways}'
            ),
            "rounding.mode 'sideways' is not one of",
            id="rounding-unknown-mode",
        ),
        pytest.param(
            BRACKETS_2025.replace("\nrounding: none", '\nrounding: {increment: "0", mode: down}'),
            "increment must be a positive",
            id="rounding-zero-increment",
        ),
        pytest.param(
            BRACKETS_2025.replace("sources:\n  - https://example.org/rates-2025", "sources: []"),
            "sources must list at least one",
            id="sources-empty",
        ),
        pytest.param("", "dataset must be a mapping", id="empty-file"),
    ],
)
def test_rejects_malformed_bracket_dataset(tmp_path: Path, content: str, message: str) -> None:
    write(tmp_path, "ex/parameters/brackets/2025.yaml", content)

    with pytest.raises(InvalidParameterDataError, match=message) as excinfo:
        source(tmp_path).get("ex/brackets", 2025, BRACKETS)

    assert "2025.yaml" in str(excinfo.value)


@pytest.mark.parametrize(
    ("content", "message"),
    [
        pytest.param(
            CREDIT_2025.replace('amount: "1000"', 'amount: "-1"'),
            "amount must not be negative",
            id="amount-negative",
        ),
        pytest.param(
            CREDIT_2025 + 'rate: "0.125"\n',
            r"unknown keys \['rate'\]",
            id="rate-is-not-a-credit-key",
        ),
        pytest.param(
            CREDIT_2025.replace('amount: "1000"', "amount: 1000"),
            "amount must be a string, got int",
            id="amount-as-yaml-number",
        ),
        pytest.param(
            CREDIT_2025.replace('amount: "1000"\n', ""),
            r"missing keys \['amount'\]",
            id="amount-missing",
        ),
    ],
)
def test_rejects_malformed_credit_dataset(tmp_path: Path, content: str, message: str) -> None:
    write(tmp_path, "ex/parameters/personal_credit/2025.yaml", content)

    with pytest.raises(InvalidParameterDataError, match=message) as excinfo:
        source(tmp_path).get("ex/personal_credit", 2025, CREDIT)

    assert "2025.yaml" in str(excinfo.value)


def test_an_invalid_credit_amount_is_reported_as_a_credit_error(tmp_path: Path) -> None:
    write(
        tmp_path,
        "ex/parameters/personal_credit/2025.yaml",
        CREDIT_2025.replace('amount: "1000"', 'amount: "-1"'),
    )

    with pytest.raises(InvalidParameterDataError) as excinfo:
        source(tmp_path).get("ex/personal_credit", 2025, CREDIT)

    assert isinstance(excinfo.value.__cause__, InvalidCreditError)


@pytest.mark.parametrize(
    ("content", "message"),
    [
        pytest.param(
            RATE_2025.replace('rate: "0.125"', 'rate: "1.5"'),
            "rate must be between 0 and 1",
            id="rate-above-one",
        ),
        pytest.param(
            RATE_2025.replace('rate: "0.125"', 'rate: "-0.1"'),
            "rate must be between 0 and 1",
            id="rate-negative",
        ),
        pytest.param(
            RATE_2025.replace('rate: "0.125"', "rate: 0.125"),
            "rate must be a string, got float",
            id="rate-as-yaml-number",
        ),
        pytest.param(
            RATE_2025.replace('rate: "0.125"', 'rate: "Infinity"'),
            "rate is not a decimal",
            id="rate-infinite",
        ),
        pytest.param(
            RATE_2025.replace('rate: "0.125"\n', ""),
            r"missing keys \['rate'\]",
            id="rate-missing",
        ),
        pytest.param(
            RATE_2025 + 'amount: "1000"\n',
            r"unknown keys \['amount'\]",
            id="amount-is-not-a-rate-key",
        ),
        pytest.param(
            RATE_2025.replace("kind: rate", "kind: credit"),
            "kind 'credit' does not match the requested 'rate'",
            id="kind-mismatch",
        ),
    ],
)
def test_rejects_malformed_rate_dataset(tmp_path: Path, content: str, message: str) -> None:
    write(tmp_path, "ex/parameters/credit_rate/2025.yaml", content)

    with pytest.raises(InvalidParameterDataError, match=message) as excinfo:
        source(tmp_path).get("ex/credit_rate", 2025, RATE)

    assert "2025.yaml" in str(excinfo.value)


def test_a_rate_out_of_range_is_reported_as_a_rate_error(tmp_path: Path) -> None:
    write(
        tmp_path,
        "ex/parameters/credit_rate/2025.yaml",
        RATE_2025.replace('rate: "0.125"', 'rate: "1.5"'),
    )

    with pytest.raises(InvalidParameterDataError) as excinfo:
        source(tmp_path).get("ex/credit_rate", 2025, RATE)

    assert isinstance(excinfo.value.__cause__, InvalidRateError)


@pytest.mark.parametrize(
    ("content", "message"),
    [
        pytest.param(
            AMOUNT_2025.replace('amount: "1471"', 'amount: "-1"'),
            "amount must not be negative",
            id="amount-negative",
        ),
        pytest.param(
            AMOUNT_2025.replace('amount: "1471"', 'amount: "-0.01"'),
            "amount must not be negative",
            id="amount-slightly-negative",
        ),
        pytest.param(
            AMOUNT_2025.replace('amount: "1471"', 'amount: "Infinity"'),
            "amount is not a decimal",
            id="amount-infinite",
        ),
        pytest.param(
            AMOUNT_2025.replace('amount: "1471"', 'amount: "NaN"'),
            "amount is not a decimal",
            id="amount-nan",
        ),
        pytest.param(
            AMOUNT_2025.replace('amount: "1471"', 'amount: "lots"'),
            "amount is not a decimal: 'lots'",
            id="amount-not-decimal",
        ),
        pytest.param(
            AMOUNT_2025.replace('amount: "1471"', "amount: 1471"),
            "amount must be a string, got int",
            id="amount-as-yaml-number",
        ),
        pytest.param(
            AMOUNT_2025.replace('amount: "1471"', "amount: 1471.5"),
            "amount must be a string, got float",
            id="amount-as-yaml-float",
        ),
        pytest.param(
            AMOUNT_2025.replace('amount: "1471"\n', ""),
            r"missing keys \['amount'\]",
            id="amount-missing",
        ),
        pytest.param(
            AMOUNT_2025 + 'rate: "0.125"\n',
            r"unknown keys \['rate'\]",
            id="rate-is-not-an-amount-key",
        ),
        pytest.param(
            AMOUNT_2025.replace("kind: amount", "kind: credit"),
            "kind 'credit' does not match the requested 'amount'",
            id="kind-mismatch",
        ),
        pytest.param(
            AMOUNT_2025.replace("kind: amount\n", ""),
            "missing key 'kind'",
            id="kind-missing",
        ),
        pytest.param(
            AMOUNT_2025.replace("rounding: none\n", ""),
            r"missing keys \['rounding'\]",
            id="rounding-missing",
        ),
        pytest.param(
            AMOUNT_2025.replace("sources:\n  - https://example.org/amount-cap-2025", "sources: []"),
            "sources must list at least one",
            id="sources-empty",
        ),
    ],
)
def test_rejects_malformed_amount_dataset(tmp_path: Path, content: str, message: str) -> None:
    write(tmp_path, "ex/parameters/amount_cap/2025.yaml", content)

    with pytest.raises(InvalidParameterDataError, match=message) as excinfo:
        source(tmp_path).get("ex/amount_cap", 2025, AMOUNT)

    assert "2025.yaml" in str(excinfo.value)


def test_a_negative_amount_is_reported_as_an_amount_error(tmp_path: Path) -> None:
    write(
        tmp_path,
        "ex/parameters/amount_cap/2025.yaml",
        AMOUNT_2025.replace('amount: "1471"', 'amount: "-1"'),
    )

    with pytest.raises(InvalidParameterDataError) as excinfo:
        source(tmp_path).get("ex/amount_cap", 2025, AMOUNT)

    assert isinstance(excinfo.value.__cause__, InvalidAmountError)


def test_reads_a_threshold_rate_dataset(tmp_path: Path) -> None:
    write(tmp_path, "ex/parameters/threshold_rate/2025.yaml", THRESHOLD_RATE_2025)

    result = source(tmp_path).get("ex/threshold_rate", 2025, THRESHOLD_RATE)

    assert result == ParameterDataset(
        family="ex/threshold_rate",
        tax_year=2025,
        kind=THRESHOLD_RATE,
        values=ThresholdRate(Rate(D("0.0505")), D("52886")),
        rounding=NO_ROUNDING,
        sources=("https://example.org/threshold-rate-2025",),
    )


def test_reads_a_threshold_rates_figures_exactly(tmp_path: Path) -> None:
    content = THRESHOLD_RATE_2025.replace('threshold: "52886"', 'threshold: "52886.50"').replace(
        'rate: "0.0505"', 'rate: "0.05050"'
    )
    write(tmp_path, "ex/parameters/threshold_rate/2025.yaml", content)

    values = source(tmp_path).get("ex/threshold_rate", 2025, THRESHOLD_RATE).values

    assert str(values.threshold) == "52886.50"
    assert str(values.rate.value) == "0.05050"  # exact, scale kept


def test_reads_a_threshold_rate_datasets_rounding_rule(tmp_path: Path) -> None:
    write(
        tmp_path,
        "ex/parameters/threshold_rate/2025.yaml",
        THRESHOLD_RATE_2025.replace(
            "rounding: none", 'rounding: {increment: "0.01", mode: half_up}'
        ),
    )

    result = source(tmp_path).get("ex/threshold_rate", 2025, THRESHOLD_RATE)

    assert result.rounding == RoundTo(D("0.01"), RoundingMode.HALF_UP)


def test_by_default_the_threshold_rate_parser_comes_from_the_shared_registry(
    tmp_path: Path,
) -> None:
    write(tmp_path, "ex/parameters/threshold_rate/2025.yaml", THRESHOLD_RATE_2025)

    result = YamlParameterSource(roots(tmp_path), built_in_parsers()).get(
        "ex/threshold_rate", 2025, THRESHOLD_RATE
    )

    assert result.values == ThresholdRate(Rate(D("0.0505")), D("52886"))


def test_a_threshold_rate_dataset_is_not_a_rate_dataset(tmp_path: Path) -> None:
    write(tmp_path, "ex/parameters/threshold_rate/2025.yaml", THRESHOLD_RATE_2025)

    with pytest.raises(InvalidParameterDataError, match="kind 'threshold_rate' does not match"):
        source(tmp_path).get("ex/threshold_rate", 2025, RATE)


@pytest.mark.parametrize(
    ("content", "message"),
    [
        pytest.param(
            THRESHOLD_RATE_2025.replace('rate: "0.0505"', 'rate: "1.5"'),
            "rate must be between 0 and 1",
            id="rate-above-one",
        ),
        pytest.param(
            THRESHOLD_RATE_2025.replace('rate: "0.0505"', 'rate: "0"'),
            "rate must not be zero",
            id="rate-zero",
        ),
        pytest.param(
            THRESHOLD_RATE_2025.replace('rate: "0.0505"', "rate: 0.0505"),
            "rate must be a string, got float",
            id="rate-as-yaml-number",
        ),
        pytest.param(
            THRESHOLD_RATE_2025.replace('threshold: "52886"', "threshold: 52886"),
            "threshold must be a string, got int",
            id="threshold-as-yaml-number",
        ),
        pytest.param(
            THRESHOLD_RATE_2025.replace('threshold: "52886"', 'threshold: "lots"'),
            "threshold is not a decimal: 'lots'",
            id="threshold-not-decimal",
        ),
        pytest.param(
            THRESHOLD_RATE_2025.replace('threshold: "52886"', 'threshold: "-1"'),
            "threshold must not be negative",
            id="threshold-negative",
        ),
        pytest.param(
            THRESHOLD_RATE_2025.replace('threshold: "52886"', 'threshold: "Infinity"'),
            "threshold is not a decimal",
            id="threshold-infinite",
        ),
        pytest.param(
            THRESHOLD_RATE_2025.replace('rate: "0.0505"\n', ""),
            r"missing keys \['rate'\]",
            id="rate-missing",
        ),
        pytest.param(
            THRESHOLD_RATE_2025.replace('threshold: "52886"\n', ""),
            r"missing keys \['threshold'\]",
            id="threshold-missing",
        ),
        pytest.param(
            THRESHOLD_RATE_2025 + 'amount: "1"\n',
            r"unknown keys \['amount'\]",
            id="unknown-key",
        ),
    ],
)
def test_rejects_an_invalid_threshold_rate_dataset(
    tmp_path: Path, content: str, message: str
) -> None:
    write(tmp_path, "ex/parameters/threshold_rate/2025.yaml", content)

    with pytest.raises(InvalidParameterDataError, match=message):
        source(tmp_path).get("ex/threshold_rate", 2025, THRESHOLD_RATE)


def test_an_invalid_threshold_rate_figure_is_reported_as_a_threshold_rate_error(
    tmp_path: Path,
) -> None:
    write(
        tmp_path,
        "ex/parameters/threshold_rate/2025.yaml",
        THRESHOLD_RATE_2025.replace('threshold: "52886"', 'threshold: "-1"'),
    )

    with pytest.raises(InvalidParameterDataError) as raised:
        source(tmp_path).get("ex/threshold_rate", 2025, THRESHOLD_RATE)

    assert isinstance(raised.value.__cause__, InvalidThresholdRateError)


def test_an_amount_dataset_is_not_a_credit_dataset(tmp_path: Path) -> None:
    # Both kinds read an `amount` key; the declared kind alone tells them apart.
    write(tmp_path, "ex/parameters/amount_cap/2025.yaml", AMOUNT_2025)

    with pytest.raises(InvalidParameterDataError, match="kind 'amount' does not match"):
        source(tmp_path).get("ex/amount_cap", 2025, CREDIT)


def test_a_credit_dataset_is_not_an_amount_dataset(tmp_path: Path) -> None:
    write(tmp_path, "ex/parameters/personal_credit/2025.yaml", CREDIT_2025)

    with pytest.raises(InvalidParameterDataError, match="kind 'credit' does not match"):
        source(tmp_path).get("ex/personal_credit", 2025, AMOUNT)


def test_reads_a_surcharge_tiers_maximum(tmp_path: Path) -> None:
    write(tmp_path, "ex/parameters/surcharge_tiers/2025.yaml", CAPPED_SURCHARGE_TIERS_2025)

    result = source(tmp_path).get("ex/surcharge_tiers", 2025, SURCHARGE_TIERS)

    assert result.values == SurchargeTiers(
        (
            SurchargeTier(D("100"), Rate(D("0.10"))),
            SurchargeTier(D("300.50"), Rate(D("0.25")), D("150.50")),
        )
    )


def test_reads_a_surcharge_tiers_maximum_exactly(tmp_path: Path) -> None:
    write(tmp_path, "ex/parameters/surcharge_tiers/2025.yaml", CAPPED_SURCHARGE_TIERS_2025)

    tiers = source(tmp_path).get("ex/surcharge_tiers", 2025, SURCHARGE_TIERS).values.tiers

    assert str(tiers[1].maximum) == "150.50"  # exact, scale kept


def test_a_surcharge_tier_without_a_maximum_reads_as_none(tmp_path: Path) -> None:
    write(tmp_path, "ex/parameters/surcharge_tiers/2025.yaml", CAPPED_SURCHARGE_TIERS_2025)

    tiers = source(tmp_path).get("ex/surcharge_tiers", 2025, SURCHARGE_TIERS).values.tiers

    assert tiers[0].maximum is None


def test_reads_a_maximum_on_every_surcharge_tier(tmp_path: Path) -> None:
    write(
        tmp_path,
        "ex/parameters/surcharge_tiers/2025.yaml",
        SURCHARGE_TIERS_2025.replace('rate: "0.10"}', 'rate: "0.10", maximum: "20"}').replace(
            'rate: "0.25"}', 'rate: "0.25", maximum: "15"}'
        ),
    )

    tiers = source(tmp_path).get("ex/surcharge_tiers", 2025, SURCHARGE_TIERS).values.tiers

    assert [tier.maximum for tier in tiers] == [D("20"), D("15")]


def test_reads_a_zero_surcharge_tier_maximum(tmp_path: Path) -> None:
    write(
        tmp_path,
        "ex/parameters/surcharge_tiers/2025.yaml",
        SURCHARGE_TIERS_2025.replace('rate: "0.10"}', 'rate: "0.10", maximum: "0"}'),
    )

    tiers = source(tmp_path).get("ex/surcharge_tiers", 2025, SURCHARGE_TIERS).values.tiers

    assert tiers[0].maximum == D("0")


def test_reads_a_surcharge_tiers_maximum_written_as_a_block_mapping(tmp_path: Path) -> None:
    write(
        tmp_path,
        "ex/parameters/surcharge_tiers/2025.yaml",
        SURCHARGE_TIERS_2025.replace(
            '  - {threshold: "300.50", rate: "0.25"}\n',
            '  - threshold: "300.50"\n    rate: "0.25"\n    maximum: "150"\n',
        ),
    )

    tiers = source(tmp_path).get("ex/surcharge_tiers", 2025, SURCHARGE_TIERS).values.tiers

    assert tiers[1] == SurchargeTier(D("300.50"), Rate(D("0.25")), D("150"))


@pytest.mark.parametrize(
    ("content", "message"),
    [
        pytest.param(
            CAPPED_SURCHARGE_TIERS_2025.replace('maximum: "150.50"', "maximum: 150"),
            r"tiers\[1\].maximum must be a string, got int",
            id="maximum-as-yaml-number",
        ),
        pytest.param(
            CAPPED_SURCHARGE_TIERS_2025.replace('maximum: "150.50"', "maximum: null"),
            r"tiers\[1\].maximum must be a string",
            id="maximum-null",
        ),
        pytest.param(
            CAPPED_SURCHARGE_TIERS_2025.replace('maximum: "150.50"', 'maximum: "lots"'),
            r"tiers\[1\].maximum is not a decimal: 'lots'",
            id="maximum-not-decimal",
        ),
        pytest.param(
            CAPPED_SURCHARGE_TIERS_2025.replace('maximum: "150.50"', 'maximum: "NaN"'),
            r"tiers\[1\].maximum is not a decimal",
            id="maximum-nan",
        ),
        pytest.param(
            CAPPED_SURCHARGE_TIERS_2025.replace('maximum: "150.50"', 'maximum: "Infinity"'),
            r"tiers\[1\].maximum is not a decimal",
            id="maximum-infinite",
        ),
        pytest.param(
            CAPPED_SURCHARGE_TIERS_2025.replace('maximum: "150.50"', 'maximum: "-0.01"'),
            r"tiers\[1\].*maximum must not be negative",
            id="maximum-negative",
        ),
        pytest.param(
            CAPPED_SURCHARGE_TIERS_2025.replace(
                'maximum: "150.50"}', 'maximum: "150.50", cap: "1"}'
            ),
            r"tiers\[1\]: unknown keys \['cap'\]",
            id="unknown-key-beside-maximum",
        ),
        pytest.param(
            CAPPED_SURCHARGE_TIERS_2025.replace('{threshold: "300.50", ', "{"),
            r"tiers\[1\]: missing keys \['threshold'\]",
            id="maximum-does-not-replace-the-threshold",
        ),
    ],
)
def test_rejects_a_malformed_surcharge_tier_maximum(
    tmp_path: Path, content: str, message: str
) -> None:
    write(tmp_path, "ex/parameters/surcharge_tiers/2025.yaml", content)

    with pytest.raises(InvalidParameterDataError, match=message) as excinfo:
        source(tmp_path).get("ex/surcharge_tiers", 2025, SURCHARGE_TIERS)

    assert "2025.yaml" in str(excinfo.value)


def test_a_negative_surcharge_tier_maximum_is_reported_as_a_surcharge_tiers_error(
    tmp_path: Path,
) -> None:
    write(
        tmp_path,
        "ex/parameters/surcharge_tiers/2025.yaml",
        CAPPED_SURCHARGE_TIERS_2025.replace('maximum: "150.50"', 'maximum: "-1"'),
    )

    with pytest.raises(InvalidParameterDataError) as excinfo:
        source(tmp_path).get("ex/surcharge_tiers", 2025, SURCHARGE_TIERS)

    assert isinstance(excinfo.value.__cause__, InvalidSurchargeTiersError)


@pytest.mark.parametrize(
    ("content", "message"),
    [
        pytest.param(
            SURCHARGE_TIERS_2025.replace(
                '  - {threshold: "100", rate: "0.10"}\n  - {threshold: "300.50", rate: "0.25"}\n',
                "  []\n",
            ),
            "at least one tier",
            id="no-tiers",
        ),
        pytest.param(
            SURCHARGE_TIERS_2025.replace('{threshold: "300.50"', '{threshold: "100"'),
            "strictly increasing",
            id="thresholds-equal",
        ),
        pytest.param(
            SURCHARGE_TIERS_2025.replace('{threshold: "300.50"', '{threshold: "50"'),
            "strictly increasing",
            id="thresholds-descending",
        ),
        pytest.param(
            SURCHARGE_TIERS_2025.replace('{threshold: "100"', '{threshold: "-1"'),
            r"tiers\[0\].*threshold must not be negative",
            id="threshold-negative",
        ),
        pytest.param(
            SURCHARGE_TIERS_2025.replace('rate: "0.25"', 'rate: "1.5"'),
            r"tiers\[1\].*rate must be between 0 and 1",
            id="rate-above-one",
        ),
        pytest.param(
            SURCHARGE_TIERS_2025.replace('rate: "0.25"', 'rate: "-0.1"'),
            r"tiers\[1\].*rate must be between 0 and 1",
            id="rate-negative",
        ),
        pytest.param(
            SURCHARGE_TIERS_2025.replace('rate: "0.25"', "rate: 0.25"),
            r"tiers\[1\].rate must be a string, got float",
            id="rate-as-yaml-number",
        ),
        pytest.param(
            SURCHARGE_TIERS_2025.replace('{threshold: "300.50"', "{threshold: 300"),
            r"tiers\[1\].threshold must be a string, got int",
            id="threshold-as-yaml-number",
        ),
        pytest.param(
            SURCHARGE_TIERS_2025.replace('{threshold: "100"', '{threshold: "lots"'),
            r"tiers\[0\].threshold is not a decimal: 'lots'",
            id="threshold-not-decimal",
        ),
        pytest.param(
            SURCHARGE_TIERS_2025.replace('rate: "0.10"', 'rate: "Infinity"'),
            r"tiers\[0\].rate is not a decimal",
            id="rate-infinite",
        ),
        pytest.param(
            SURCHARGE_TIERS_2025.replace('{threshold: "100", rate: "0.10"}', '{rate: "0.10"}'),
            r"tiers\[0\]: missing keys \['threshold'\]",
            id="threshold-missing",
        ),
        pytest.param(
            SURCHARGE_TIERS_2025.replace('rate: "0.25"}', 'rate: "0.25", from: "0"}'),
            r"tiers\[1\]: unknown keys \['from'\]",
            id="unknown-tier-key",
        ),
        pytest.param(
            SURCHARGE_TIERS_2025.replace('  - {threshold: "100", rate: "0.10"}', '  - "100"'),
            r"tiers\[0\] must be a mapping",
            id="tier-not-a-mapping",
        ),
        pytest.param(
            SURCHARGE_TIERS_2025.replace(
                '  - {threshold: "100", rate: "0.10"}\n  - {threshold: "300.50", rate: "0.25"}\n',
                '  {threshold: "100", rate: "0.10"}\n',
            ),
            "tiers must be a list",
            id="tiers-not-a-list",
        ),
        pytest.param(
            SURCHARGE_TIERS_2025.replace("tiers:", "brackets:"),
            r"unknown keys \['brackets'\]",
            id="brackets-are-not-tiers",
        ),
        pytest.param(
            SURCHARGE_TIERS_2025 + 'rate: "0.125"\n',
            r"unknown keys \['rate'\]",
            id="rate-is-not-a-surcharge-tiers-key",
        ),
        pytest.param(
            SURCHARGE_TIERS_2025.replace("kind: surcharge_tiers", "kind: brackets"),
            "kind 'brackets' does not match the requested 'surcharge_tiers'",
            id="kind-mismatch",
        ),
        pytest.param(
            SURCHARGE_TIERS_2025.replace("rounding: none\n", ""),
            r"missing keys \['rounding'\]",
            id="rounding-missing",
        ),
        pytest.param(
            SURCHARGE_TIERS_2025.replace(
                "sources:\n  - https://example.org/surcharge-2025", "sources: []"
            ),
            "sources must list at least one",
            id="sources-empty",
        ),
    ],
)
def test_rejects_malformed_surcharge_tiers_dataset(
    tmp_path: Path, content: str, message: str
) -> None:
    write(tmp_path, "ex/parameters/surcharge_tiers/2025.yaml", content)

    with pytest.raises(InvalidParameterDataError, match=message) as excinfo:
        source(tmp_path).get("ex/surcharge_tiers", 2025, SURCHARGE_TIERS)

    assert "2025.yaml" in str(excinfo.value)


def test_invalid_tiers_are_reported_as_a_surcharge_tiers_error(tmp_path: Path) -> None:
    write(
        tmp_path,
        "ex/parameters/surcharge_tiers/2025.yaml",
        SURCHARGE_TIERS_2025.replace('{threshold: "300.50"', '{threshold: "50"'),
    )

    with pytest.raises(InvalidParameterDataError) as excinfo:
        source(tmp_path).get("ex/surcharge_tiers", 2025, SURCHARGE_TIERS)

    assert isinstance(excinfo.value.__cause__, InvalidSurchargeTiersError)


def test_a_surcharge_tiers_dataset_is_not_a_bracket_dataset(tmp_path: Path) -> None:
    write(tmp_path, "ex/parameters/surcharge_tiers/2025.yaml", SURCHARGE_TIERS_2025)

    with pytest.raises(InvalidParameterDataError, match="kind 'surcharge_tiers' does not match"):
        source(tmp_path).get("ex/surcharge_tiers", 2025, BRACKETS)


@pytest.mark.parametrize(
    ("content", "message"),
    [
        pytest.param(
            FACTOR_2025.replace('value: "2"', 'value: "-1"'),
            "factor must not be negative",
            id="value-negative",
        ),
        pytest.param(
            FACTOR_2025.replace('value: "2"', 'value: "-0.01"'),
            "factor must not be negative",
            id="value-slightly-negative",
        ),
        pytest.param(
            FACTOR_2025.replace('value: "2"', 'value: "Infinity"'),
            "value is not a decimal",
            id="value-infinite",
        ),
        pytest.param(
            FACTOR_2025.replace('value: "2"', 'value: "NaN"'),
            "value is not a decimal",
            id="value-nan",
        ),
        pytest.param(
            FACTOR_2025.replace('value: "2"', 'value: "twice"'),
            "value is not a decimal: 'twice'",
            id="value-not-decimal",
        ),
        pytest.param(
            FACTOR_2025.replace('value: "2"', "value: 2"),
            "value must be a string, got int",
            id="value-as-yaml-number",
        ),
        pytest.param(
            FACTOR_2025.replace('value: "2"', "value: 2.5"),
            "value must be a string, got float",
            id="value-as-yaml-float",
        ),
        pytest.param(
            FACTOR_2025.replace('value: "2"\n', ""),
            r"missing keys \['value'\]",
            id="value-missing",
        ),
        pytest.param(
            FACTOR_2025.replace('value: "2"', 'factor: "2"'),
            r"unknown keys \['factor'\]",
            id="factor-instead-of-value",
        ),
        pytest.param(
            FACTOR_2025 + 'rate: "0.5"\n',
            r"unknown keys \['rate'\]",
            id="rate-is-not-a-factor-key",
        ),
        pytest.param(
            FACTOR_2025.replace("kind: factor", "kind: rate"),
            "kind 'rate' does not match the requested 'factor'",
            id="kind-mismatch",
        ),
        pytest.param(
            FACTOR_2025.replace("rounding: none\n", ""),
            r"missing keys \['rounding'\]",
            id="rounding-missing",
        ),
        pytest.param(
            FACTOR_2025.replace("sources:\n  - https://example.org/factor-2025", "sources: []"),
            "sources must list at least one",
            id="sources-empty",
        ),
    ],
)
def test_rejects_malformed_factor_dataset(tmp_path: Path, content: str, message: str) -> None:
    write(tmp_path, "ex/parameters/factor/2025.yaml", content)

    with pytest.raises(InvalidParameterDataError, match=message) as excinfo:
        source(tmp_path).get("ex/factor", 2025, FACTOR)

    assert "2025.yaml" in str(excinfo.value)


def test_a_negative_factor_is_reported_as_a_factor_error(tmp_path: Path) -> None:
    write(
        tmp_path,
        "ex/parameters/factor/2025.yaml",
        FACTOR_2025.replace('value: "2"', 'value: "-1"'),
    )

    with pytest.raises(InvalidParameterDataError) as excinfo:
        source(tmp_path).get("ex/factor", 2025, FACTOR)

    assert isinstance(excinfo.value.__cause__, InvalidFactorError)


def test_a_rate_dataset_is_not_a_factor_dataset(tmp_path: Path) -> None:
    write(tmp_path, "ex/parameters/credit_rate/2025.yaml", RATE_2025)

    with pytest.raises(InvalidParameterDataError, match="kind 'rate' does not match"):
        source(tmp_path).get("ex/credit_rate", 2025, FACTOR)


def test_a_factor_dataset_is_not_an_amount_dataset(tmp_path: Path) -> None:
    write(tmp_path, "ex/parameters/factor/2025.yaml", FACTOR_2025)

    with pytest.raises(InvalidParameterDataError, match="kind 'factor' does not match"):
        source(tmp_path).get("ex/factor", 2025, AMOUNT)


@pytest.mark.parametrize(
    ("content", "message"),
    [
        pytest.param(
            FRACTION_2025.replace('denominator: "3"', 'denominator: "0"'),
            "fraction denominator must be positive",
            id="denominator-zero",
        ),
        pytest.param(
            FRACTION_2025.replace('numerator: "2"', 'numerator: "-2"'),
            "numerator is not a whole number: '-2'",
            id="numerator-negative",
        ),
        pytest.param(
            FRACTION_2025.replace('denominator: "3"', 'denominator: "-3"'),
            "denominator is not a whole number: '-3'",
            id="denominator-negative",
        ),
        pytest.param(
            FRACTION_2025.replace('numerator: "2"', 'numerator: "2.5"'),
            "numerator is not a whole number: '2.5'",
            id="numerator-not-whole",
        ),
        pytest.param(
            FRACTION_2025.replace('denominator: "3"', 'denominator: "3.0"'),
            "denominator is not a whole number: '3.0'",
            id="denominator-with-a-decimal-point",
        ),
        pytest.param(
            FRACTION_2025.replace('numerator: "2"', 'numerator: "NaN"'),
            "numerator is not a whole number: 'NaN'",
            id="numerator-nan",
        ),
        pytest.param(
            FRACTION_2025.replace('denominator: "3"', 'denominator: "Infinity"'),
            "denominator is not a whole number: 'Infinity'",
            id="denominator-infinite",
        ),
        pytest.param(
            FRACTION_2025.replace('numerator: "2"', 'numerator: "two"'),
            "numerator is not a whole number: 'two'",
            id="numerator-words",
        ),
        pytest.param(
            FRACTION_2025.replace('numerator: "2"', 'numerator: "+2"'),
            r"numerator is not a whole number: '\+2'",
            id="numerator-signed",
        ),
        pytest.param(
            FRACTION_2025.replace('denominator: "3"', 'denominator: "03"'),
            "denominator is not a whole number: '03'",
            id="denominator-leading-zero",
        ),
        pytest.param(
            FRACTION_2025.replace('denominator: "3"', 'denominator: " 3"'),
            "denominator is not a whole number: ' 3'",
            id="denominator-padded",
        ),
        pytest.param(
            FRACTION_2025.replace('denominator: "3"', 'denominator: "1_000"'),
            "denominator is not a whole number: '1_000'",
            id="denominator-underscored",
        ),
        pytest.param(
            FRACTION_2025.replace('numerator: "2"', 'numerator: "\u0662"'),
            "numerator is not a whole number",
            id="numerator-non-ascii-digit",
        ),
        pytest.param(
            FRACTION_2025.replace('numerator: "2"', 'numerator: ""'),
            "numerator is not a whole number: ''",
            id="numerator-empty",
        ),
        pytest.param(
            FRACTION_2025.replace('numerator: "2"', "numerator: 2"),
            "numerator must be a string, got int",
            id="numerator-as-yaml-number",
        ),
        pytest.param(
            FRACTION_2025.replace('denominator: "3"', "denominator: 3"),
            "denominator must be a string, got int",
            id="denominator-as-yaml-number",
        ),
        pytest.param(
            FRACTION_2025.replace('numerator: "2"', "numerator: 2.5"),
            "numerator must be a string, got float",
            id="numerator-as-yaml-float",
        ),
        pytest.param(
            FRACTION_2025.replace('denominator: "3"\n', ""),
            r"missing keys \['denominator'\]",
            id="denominator-missing",
        ),
        pytest.param(
            FRACTION_2025.replace('numerator: "2"\n', "").replace('denominator: "3"\n', ""),
            r"missing keys \['denominator', 'numerator'\]",
            id="both-parts-missing",
        ),
        pytest.param(
            FRACTION_2025.replace('numerator: "2"\ndenominator: "3"', 'value: "2/3"'),
            r"unknown keys \['value'\]",
            id="value-instead-of-parts",
        ),
        pytest.param(
            FRACTION_2025 + 'rate: "0.5"\n',
            r"unknown keys \['rate'\]",
            id="rate-is-not-a-fraction-key",
        ),
        pytest.param(
            FRACTION_2025.replace("kind: fraction", "kind: rate"),
            "kind 'rate' does not match the requested 'fraction'",
            id="kind-mismatch",
        ),
        pytest.param(
            FRACTION_2025.replace("rounding: none\n", ""),
            r"missing keys \['rounding'\]",
            id="rounding-missing",
        ),
        pytest.param(
            FRACTION_2025.replace("sources:\n  - https://example.org/fraction-2025", "sources: []"),
            "sources must list at least one",
            id="sources-empty",
        ),
    ],
)
def test_rejects_malformed_fraction_dataset(tmp_path: Path, content: str, message: str) -> None:
    write(tmp_path, "ex/parameters/fraction/2025.yaml", content)

    with pytest.raises(InvalidParameterDataError, match=message) as excinfo:
        source(tmp_path).get("ex/fraction", 2025, FRACTION)

    assert "2025.yaml" in str(excinfo.value)


def test_rejects_a_part_too_long_for_a_whole_number(tmp_path: Path) -> None:
    # 4,301 digits: one more than `int()` converts from text by default.
    part = "1" + "0" * 4300
    write(
        tmp_path,
        "ex/parameters/fraction/2025.yaml",
        FRACTION_2025.replace('numerator: "2"', f'numerator: "{part}"'),
    )

    with pytest.raises(
        InvalidParameterDataError, match="numerator is not a whole number"
    ) as excinfo:
        source(tmp_path).get("ex/fraction", 2025, FRACTION)

    assert "2025.yaml" in str(excinfo.value)


@pytest.mark.parametrize(
    ("old", "new"),
    [
        ('denominator: "3"', 'denominator: "0"'),
        ('numerator: "2"\ndenominator: "3"', 'numerator: "0"\ndenominator: "0"'),
    ],
)
def test_a_zero_denominator_is_reported_as_a_fraction_error(
    tmp_path: Path, old: str, new: str
) -> None:
    content = FRACTION_2025.replace(old, new)
    assert content != FRACTION_2025
    write(tmp_path, "ex/parameters/fraction/2025.yaml", content)

    with pytest.raises(InvalidParameterDataError) as excinfo:
        source(tmp_path).get("ex/fraction", 2025, FRACTION)

    assert isinstance(excinfo.value.__cause__, InvalidFractionError)


def test_a_rate_dataset_is_not_a_fraction_dataset(tmp_path: Path) -> None:
    write(tmp_path, "ex/parameters/credit_rate/2025.yaml", RATE_2025)

    with pytest.raises(InvalidParameterDataError, match="kind 'rate' does not match"):
        source(tmp_path).get("ex/credit_rate", 2025, FRACTION)


def test_a_fraction_dataset_is_not_a_rate_dataset(tmp_path: Path) -> None:
    write(tmp_path, "ex/parameters/fraction/2025.yaml", FRACTION_2025)

    with pytest.raises(InvalidParameterDataError, match="kind 'fraction' does not match"):
        source(tmp_path).get("ex/fraction", 2025, RATE)


#
# A `rate_table` dataset holds `rate_at_zero` and `rows`, each row a `more_than`, a `rate` and,
# on every row but the last, a `not_more_than`, all quoted decimals.

RATE_TABLE_ROWS = (
    RateTableRow(D("0"), D("1000"), Rate(D("0.30"))),
    RateTableRow(D("1000"), D("2500.50"), Rate(D("0.20"))),
    RateTableRow(D("2500.50"), None, Rate(D("0"))),
)


def test_reads_a_rate_table_dataset(tmp_path: Path) -> None:
    write(tmp_path, "ex/parameters/rate_table/2025.yaml", RATE_TABLE_2025)

    result = source(tmp_path).get("ex/rate_table", 2025, RATE_TABLE)

    assert result == ParameterDataset(
        family="ex/rate_table",
        tax_year=2025,
        kind=RATE_TABLE,
        values=RateTable(rate_at_zero=Rate(D("0.30")), rows=RATE_TABLE_ROWS),
        rounding=NO_ROUNDING,
        sources=("https://example.org/rate-table-2025",),
    )


def test_reads_a_rate_tables_figures_exactly(tmp_path: Path) -> None:
    write(tmp_path, "ex/parameters/rate_table/2025.yaml", RATE_TABLE_2025)

    table = source(tmp_path).get("ex/rate_table", 2025, RATE_TABLE).values

    assert str(table.rate_at_zero.value) == "0.30"
    assert [str(row.more_than) for row in table.rows] == ["0", "1000", "2500.50"]
    assert [
        None if row.not_more_than is None else str(row.not_more_than) for row in table.rows
    ] == [
        "1000",
        "2500.50",
        None,
    ]
    assert [str(row.rate.value) for row in table.rows] == ["0.30", "0.20", "0"]


def test_reads_a_single_unbounded_row(tmp_path: Path) -> None:
    content = RATE_TABLE_2025.replace(
        '  - {more_than: "0", not_more_than: "1000", rate: "0.30"}\n'
        '  - {more_than: "1000", not_more_than: "2500.50", rate: "0.20"}\n'
        '  - {more_than: "2500.50", rate: "0"}\n',
        '  - {more_than: "0", rate: "0.30"}\n',
    )
    write(tmp_path, "ex/parameters/rate_table/2025.yaml", content)

    table = source(tmp_path).get("ex/rate_table", 2025, RATE_TABLE).values

    assert table.rows == (RateTableRow(D("0"), None, Rate(D("0.30"))),)


def test_reads_an_overlap_as_printed(tmp_path: Path) -> None:
    content = RATE_TABLE_2025.replace('not_more_than: "2500.50"', 'not_more_than: "2600"')
    write(tmp_path, "ex/parameters/rate_table/2025.yaml", content)

    table = source(tmp_path).get("ex/rate_table", 2025, RATE_TABLE).values

    assert table.rows[1] == RateTableRow(D("1000"), D("2600"), Rate(D("0.20")))


def test_reads_a_rate_table_written_as_block_mappings(tmp_path: Path) -> None:
    content = RATE_TABLE_2025.replace(
        '  - {more_than: "2500.50", rate: "0"}\n',
        '  - more_than: "2500.50"\n    rate: "0"\n',
    )
    write(tmp_path, "ex/parameters/rate_table/2025.yaml", content)

    table = source(tmp_path).get("ex/rate_table", 2025, RATE_TABLE).values

    assert table.rows == RATE_TABLE_ROWS


def test_reads_a_rate_table_datasets_rounding_rule(tmp_path: Path) -> None:
    write(
        tmp_path,
        "ex/parameters/rate_table/2025.yaml",
        RATE_TABLE_2025.replace("rounding: none", 'rounding: {increment: "0.01", mode: half_up}'),
    )

    result = source(tmp_path).get("ex/rate_table", 2025, RATE_TABLE)

    assert result.rounding == RoundTo(D("0.01"), RoundingMode.HALF_UP)


def test_by_default_the_rate_table_parser_comes_from_the_shared_registry(tmp_path: Path) -> None:
    write(tmp_path, "ex/parameters/rate_table/2025.yaml", RATE_TABLE_2025)

    result = YamlParameterSource(roots(tmp_path), built_in_parsers()).get(
        "ex/rate_table", 2025, RATE_TABLE
    )

    assert result.values == RateTable(Rate(D("0.30")), RATE_TABLE_ROWS)


@pytest.mark.parametrize(
    ("content", "message"),
    [
        pytest.param(
            RATE_TABLE_2025.replace('rate_at_zero: "0.30"', "rate_at_zero: 0.30"),
            "rate_at_zero must be a string, got float",
            id="rate-at-zero-as-yaml-number",
        ),
        pytest.param(
            RATE_TABLE_2025.replace('rate_at_zero: "0.30"', 'rate_at_zero: "1.5"'),
            "rate must be between 0 and 1",
            id="rate-at-zero-above-one",
        ),
        pytest.param(
            RATE_TABLE_2025.replace('rate_at_zero: "0.30"\n', ""),
            r"missing keys \['rate_at_zero'\]",
            id="rate-at-zero-missing",
        ),
        pytest.param(
            RATE_TABLE_2025.replace('rate: "0.20"', 'rate: "1.5"'),
            r"rows\[1\].*rate must be between 0 and 1",
            id="row-rate-above-one",
        ),
        pytest.param(
            RATE_TABLE_2025.replace('rate: "0.20"', "rate: 0.20"),
            r"rows\[1\].rate must be a string, got float",
            id="row-rate-as-yaml-number",
        ),
        pytest.param(
            RATE_TABLE_2025.replace('{more_than: "1000"', "{more_than: 1000"),
            r"rows\[1\].more_than must be a string, got int",
            id="more-than-as-yaml-number",
        ),
        pytest.param(
            RATE_TABLE_2025.replace('not_more_than: "1000"', 'not_more_than: "lots"'),
            r"rows\[0\].not_more_than is not a decimal: 'lots'",
            id="not-more-than-not-decimal",
        ),
        pytest.param(
            RATE_TABLE_2025.replace('{more_than: "0", not_more_than', "{not_more_than"),
            r"rows\[0\]: missing keys \['more_than'\]",
            id="more-than-missing",
        ),
        pytest.param(
            RATE_TABLE_2025.replace(', rate: "0.30"}', "}"),
            r"rows\[0\]: missing keys \['rate'\]",
            id="row-rate-missing",
        ),
        pytest.param(
            RATE_TABLE_2025.replace('rate: "0"}', 'rate: "0", threshold: "0"}'),
            r"rows\[2\]: unknown keys \['threshold'\]",
            id="unknown-row-key",
        ),
        pytest.param(
            RATE_TABLE_2025.replace(
                '  - {more_than: "0", not_more_than: "1000", rate: "0.30"}', '  - "0"'
            ),
            r"rows\[0\] must be a mapping",
            id="row-not-a-mapping",
        ),
        pytest.param(
            RATE_TABLE_2025.split("rows:\n")[0] + "rows: []\n",
            "at least one row",
            id="no-rows",
        ),
        pytest.param(
            RATE_TABLE_2025.replace('{more_than: "0",', '{more_than: "100",'),
            "first row must be more than 0",
            id="first-row-not-zero",
        ),
        pytest.param(
            RATE_TABLE_2025.replace('{more_than: "1000"', '{more_than: "0"'),
            "strictly increasing",
            id="more-than-not-increasing",
        ),
        pytest.param(
            RATE_TABLE_2025.replace('not_more_than: "1000"', 'not_more_than: "900"'),
            "gap between 900 and 1000",
            id="gap",
        ),
        pytest.param(
            RATE_TABLE_2025.replace('not_more_than: "2500.50", ', ""),
            "every row but the last must have",
            id="upper-bound-missing-before-the-last",
        ),
        pytest.param(
            RATE_TABLE_2025.replace(
                '{more_than: "2500.50", rate', '{more_than: "2500.50", not_more_than: "5000", rate'
            ),
            "last row must have no not_more_than",
            id="upper-bound-on-the-last",
        ),
        pytest.param(
            RATE_TABLE_2025.replace("rows:", "tiers:"),
            r"unknown keys \['tiers'\]",
            id="tiers-are-not-rows",
        ),
        pytest.param(
            RATE_TABLE_2025.replace("kind: rate_table", "kind: rate"),
            "kind 'rate' does not match the requested 'rate_table'",
            id="kind-mismatch",
        ),
        pytest.param(
            RATE_TABLE_2025.replace("rounding: none\n", ""),
            r"missing keys \['rounding'\]",
            id="rounding-missing",
        ),
        pytest.param(
            RATE_TABLE_2025.replace(
                "sources:\n  - https://example.org/rate-table-2025", "sources: []"
            ),
            "sources must list at least one",
            id="sources-empty",
        ),
    ],
)
def test_rejects_malformed_rate_table_dataset(tmp_path: Path, content: str, message: str) -> None:
    write(tmp_path, "ex/parameters/rate_table/2025.yaml", content)

    with pytest.raises(InvalidParameterDataError, match=message) as excinfo:
        source(tmp_path).get("ex/rate_table", 2025, RATE_TABLE)

    assert "2025.yaml" in str(excinfo.value)


@pytest.mark.parametrize(
    ("old", "new"),
    [
        ('{more_than: "0",', '{more_than: "100",'),
        ('{more_than: "1000"', '{more_than: "0"'),
        ('not_more_than: "1000"', 'not_more_than: "900"'),
        ('not_more_than: "2500.50", ', ""),
    ],
)
def test_an_invalid_rate_table_is_reported_as_a_rate_table_error(
    tmp_path: Path, old: str, new: str
) -> None:
    write(tmp_path, "ex/parameters/rate_table/2025.yaml", RATE_TABLE_2025.replace(old, new))

    with pytest.raises(InvalidParameterDataError) as excinfo:
        source(tmp_path).get("ex/rate_table", 2025, RATE_TABLE)

    assert isinstance(excinfo.value.__cause__, InvalidRateTableError)


def test_a_surcharge_tiers_dataset_is_not_a_rate_table_dataset(tmp_path: Path) -> None:
    write(tmp_path, "ex/parameters/surcharge_tiers/2025.yaml", SURCHARGE_TIERS_2025)

    with pytest.raises(InvalidParameterDataError, match="kind 'surcharge_tiers' does not match"):
        source(tmp_path).get("ex/surcharge_tiers", 2025, RATE_TABLE)


def test_a_rate_table_dataset_is_not_a_rate_dataset(tmp_path: Path) -> None:
    write(tmp_path, "ex/parameters/rate_table/2025.yaml", RATE_TABLE_2025)

    with pytest.raises(InvalidParameterDataError, match="kind 'rate_table' does not match"):
        source(tmp_path).get("ex/rate_table", 2025, RATE)


#
# A `class_rates` dataset holds `classes`, a mapping keyed by each class number as printed (a
# quoted decimal), each class a quoted decimal `rate`, a `half_year_rule` of `applies` or
# `exempt`, a `recapture_and_terminal_loss` of `applies` or `excluded`, a `half_year_rule_on_sale`
# of `applies` or `does_not_apply`, and an `aiip_factor` and a `riip_factor`, each a quoted whole
# `numerator` (0 or more) and `denominator` (above 0). It also holds `full_year_days`, a quoted
# whole number above 0: the days of a full fiscal period ("compared to 365 days").

APPLIES = HalfYearRule.APPLIES


EXEMPT = HalfYearRule.EXEMPT


INCLUDED = RecaptureAndTerminalLoss.APPLIES


EXCLUDED = RecaptureAndTerminalLoss.EXCLUDED


ON_SALE = HalfYearRuleOnSale.APPLIES


NOT_ON_SALE = HalfYearRuleOnSale.DOES_NOT_APPLY


F = Fraction


CLASS_RATES_CLASSES = (
    ClassRate(D("8"), Rate(D("0.20")), APPLIES, INCLUDED, F(0, 1), F(1, 2), NOT_ON_SALE),
    ClassRate(D("10.1"), Rate(D("0.30")), APPLIES, EXCLUDED, F(0, 1), F(1, 2), ON_SALE),
    ClassRate(D("43.1"), Rate(D("0.30")), APPLIES, INCLUDED, F(3, 2), F(7, 3), NOT_ON_SALE),
    ClassRate(D("12"), Rate(D("1")), EXEMPT, INCLUDED, F(0, 1), F(0, 1), NOT_ON_SALE),
)


def test_reads_a_class_rates_dataset(tmp_path: Path) -> None:
    write(tmp_path, "ex/parameters/class_rates/2025.yaml", CLASS_RATES_2025)

    result = source(tmp_path).get("ex/class_rates", 2025, CLASS_RATES)

    assert result == ParameterDataset(
        family="ex/class_rates",
        tax_year=2025,
        kind=CLASS_RATES,
        values=ClassRates(
            classes=CLASS_RATES_CLASSES, full_year_days=365, longest_fiscal_period_days=366
        ),
        rounding=NO_ROUNDING,
        sources=("https://example.org/class-rates-2025",),
    )


def test_reads_the_classes_in_the_files_order(tmp_path: Path) -> None:
    write(tmp_path, "ex/parameters/class_rates/2025.yaml", CLASS_RATES_2025)

    table = source(tmp_path).get("ex/class_rates", 2025, CLASS_RATES).values

    assert [str(each.class_number) for each in table.classes] == ["8", "10.1", "43.1", "12"]


def test_reads_class_numbers_and_rates_exactly(tmp_path: Path) -> None:
    write(tmp_path, "ex/parameters/class_rates/2025.yaml", CLASS_RATES_2025)

    table = source(tmp_path).get("ex/class_rates", 2025, CLASS_RATES).values

    assert [str(each.rate.value) for each in table.classes] == ["0.20", "0.30", "0.30", "1"]
    assert table.for_class(D("10.1")) == CLASS_RATES_CLASSES[1]


def test_reads_factors_as_fractions_kept_as_written(tmp_path: Path) -> None:
    write(tmp_path, "ex/parameters/class_rates/2025.yaml", CLASS_RATES_2025)

    table = source(tmp_path).get("ex/class_rates", 2025, CLASS_RATES).values

    assert [each.aiip_factor for each in table.classes] == [F(0, 1), F(0, 1), F(3, 2), F(0, 1)]
    assert [each.riip_factor for each in table.classes] == [F(1, 2), F(1, 2), F(7, 3), F(0, 1)]
    assert all(type(each.aiip_factor) is Fraction for each in table.classes)
    assert all(type(each.riip_factor) is Fraction for each in table.classes)


def test_reads_a_factor_unreduced(tmp_path: Path) -> None:
    content = CLASS_RATES_2025.replace(
        'riip_factor: {numerator: "7", denominator: "3"}',
        'riip_factor: {numerator: "14", denominator: "6"}',
    ).replace(
        'aiip_factor: {numerator: "3", denominator: "2"}',
        'aiip_factor: {numerator: "0", denominator: "2"}',
    )
    write(tmp_path, "ex/parameters/class_rates/2025.yaml", content)

    table = source(tmp_path).get("ex/class_rates", 2025, CLASS_RATES).values

    assert table.classes[2].riip_factor == F(14, 6)
    assert table.classes[2].aiip_factor == F(0, 2)


def test_reads_a_whole_factor(tmp_path: Path) -> None:
    content = CLASS_RATES_2025.replace(
        'aiip_factor: {numerator: "3", denominator: "2"}',
        'aiip_factor: {numerator: "3", denominator: "1"}',
    )
    write(tmp_path, "ex/parameters/class_rates/2025.yaml", content)

    table = source(tmp_path).get("ex/class_rates", 2025, CLASS_RATES).values

    assert table.classes[2].aiip_factor == F(3, 1)


def test_a_class_states_whether_it_has_the_half_year_rule_on_sale(tmp_path: Path) -> None:
    write(tmp_path, "ex/parameters/class_rates/2025.yaml", CLASS_RATES_2025)

    table = source(tmp_path).get("ex/class_rates", 2025, CLASS_RATES).values

    assert [entry.half_year_rule_on_sale for entry in table.classes] == [
        NOT_ON_SALE,
        ON_SALE,
        NOT_ON_SALE,
        NOT_ON_SALE,
    ]


def test_reads_a_class_that_says_the_half_year_rule_on_sale_does_not_apply(
    tmp_path: Path,
) -> None:
    content = CLASS_RATES_2025.replace(
        "half_year_rule_on_sale: applies", "half_year_rule_on_sale: does_not_apply"
    )
    write(tmp_path, "ex/parameters/class_rates/2025.yaml", content)

    table = source(tmp_path).get("ex/class_rates", 2025, CLASS_RATES).values

    assert table.for_class(D("10.1")) == ClassRate(
        D("10.1"),
        Rate(D("0.30")),
        APPLIES,
        EXCLUDED,
        F(0, 1),
        F(1, 2),
        NOT_ON_SALE,
    )


def test_reads_a_single_class(tmp_path: Path) -> None:
    content = CLASS_RATES_2025.split('  "10.1":\n')[0]
    write(tmp_path, "ex/parameters/class_rates/2025.yaml", content)

    table = source(tmp_path).get("ex/class_rates", 2025, CLASS_RATES).values

    assert table.classes == (CLASS_RATES_CLASSES[0],)


def test_reads_a_class_written_as_a_flow_mapping(tmp_path: Path) -> None:
    content = CLASS_RATES_2025.split('  "10.1":\n')[0].replace(
        '  "8":\n'
        '    rate: "0.20"\n'
        "    half_year_rule: applies\n"
        "    recapture_and_terminal_loss: applies\n"
        "    half_year_rule_on_sale: does_not_apply\n"
        '    aiip_factor: {numerator: "0", denominator: "1"}\n'
        '    riip_factor: {numerator: "1", denominator: "2"}\n',
        '  "8": {rate: "0.20", half_year_rule: applies, recapture_and_terminal_loss: applies, '
        "half_year_rule_on_sale: does_not_apply, "
        'aiip_factor: {numerator: "0", denominator: "1"}, '
        'riip_factor: {numerator: "1", denominator: "2"}}\n',
    )
    write(tmp_path, "ex/parameters/class_rates/2025.yaml", content)

    table = source(tmp_path).get("ex/class_rates", 2025, CLASS_RATES).values

    assert table.classes == (CLASS_RATES_CLASSES[0],)


def test_reads_the_days_in_a_full_year(tmp_path: Path) -> None:
    write(tmp_path, "ex/parameters/class_rates/2025.yaml", CLASS_RATES_2025)

    table = source(tmp_path).get("ex/class_rates", 2025, CLASS_RATES).values

    assert table.full_year_days == 365
    assert type(table.full_year_days) is int


def test_reads_the_days_in_a_full_year_as_written(tmp_path: Path) -> None:
    content = CLASS_RATES_2025.replace('full_year_days: "365"', 'full_year_days: "366"')
    write(tmp_path, "ex/parameters/class_rates/2025.yaml", content)

    table = source(tmp_path).get("ex/class_rates", 2025, CLASS_RATES).values

    assert table.full_year_days == 366


def test_reads_a_class_rates_datasets_rounding_rule(tmp_path: Path) -> None:
    write(
        tmp_path,
        "ex/parameters/class_rates/2025.yaml",
        CLASS_RATES_2025.replace("rounding: none", 'rounding: {increment: "0.01", mode: half_up}'),
    )

    result = source(tmp_path).get("ex/class_rates", 2025, CLASS_RATES)

    assert result.rounding == RoundTo(D("0.01"), RoundingMode.HALF_UP)


def test_by_default_the_class_rates_parser_comes_from_the_shared_registry(tmp_path: Path) -> None:
    write(tmp_path, "ex/parameters/class_rates/2025.yaml", CLASS_RATES_2025)

    result = YamlParameterSource(roots(tmp_path), built_in_parsers()).get(
        "ex/class_rates", 2025, CLASS_RATES
    )

    assert result.values == ClassRates(CLASS_RATES_CLASSES, 365, 366)


@pytest.mark.parametrize(
    ("content", "message"),
    [
        pytest.param(
            CLASS_RATES_2025.replace('rate: "0.20"', "rate: 0.20"),
            r"classes\.8\.rate must be a string, got float",
            id="rate-as-yaml-number",
        ),
        pytest.param(
            CLASS_RATES_2025.replace('rate: "0.20"', 'rate: "1.5"'),
            "rate must be between 0 and 1",
            id="rate-above-one",
        ),
        pytest.param(
            CLASS_RATES_2025.replace('rate: "0.20"', 'rate: "lots"'),
            r"classes\.8\.rate is not a decimal: 'lots'",
            id="rate-not-decimal",
        ),
        pytest.param(
            CLASS_RATES_2025.replace('  "8":\n    rate: "0.20"\n', '  "8":\n'),
            r"classes\.8: missing keys \['rate'\]",
            id="rate-missing",
        ),
        pytest.param(
            CLASS_RATES_2025.replace("half_year_rule: exempt", "half_year_rule: sometimes"),
            r"classes\.12\.half_year_rule 'sometimes' is not one of \['applies', 'exempt'\]",
            id="half-year-rule-unknown",
        ),
        pytest.param(
            CLASS_RATES_2025.replace("half_year_rule: exempt", "half_year_rule: true"),
            r"classes\.12\.half_year_rule must be a string, got bool",
            id="half-year-rule-as-yaml-bool",
        ),
        pytest.param(
            CLASS_RATES_2025.replace(
                "recapture_and_terminal_loss: excluded", "recapture_and_terminal_loss: exempt"
            ),
            r"classes\.10\.1\.recapture_and_terminal_loss 'exempt' is not one of "
            r"\['applies', 'excluded'\]",
            id="recapture-and-terminal-loss-unknown",
        ),
        pytest.param(
            CLASS_RATES_2025.replace(
                "half_year_rule_on_sale: applies", "half_year_rule_on_sale: sometimes"
            ),
            r"classes\.10\.1\.half_year_rule_on_sale 'sometimes' is not one of "
            r"\['applies', 'does_not_apply'\]",
            id="half-year-rule-on-sale-unknown",
        ),
        pytest.param(
            CLASS_RATES_2025.replace(
                "half_year_rule_on_sale: applies", "half_year_rule_on_sale: true"
            ),
            r"classes\.10\.1\.half_year_rule_on_sale must be a string, got bool",
            id="half-year-rule-on-sale-as-yaml-bool",
        ),
        pytest.param(
            CLASS_RATES_2025.replace("    recapture_and_terminal_loss: excluded\n", ""),
            r"classes\.10\.1: missing keys \['recapture_and_terminal_loss'\]",
            id="recapture-and-terminal-loss-missing",
        ),
        pytest.param(
            CLASS_RATES_2025.replace("    half_year_rule_on_sale: applies\n", ""),
            r"classes\.10\.1: missing keys \['half_year_rule_on_sale'\]",
            id="half-year-rule-on-sale-missing",
        ),
        pytest.param(
            CLASS_RATES_2025.replace(
                "    half_year_rule: exempt\n", '    half_year_rule: exempt\n    maximum: "0"\n'
            ),
            r"classes\.12: unknown keys \['maximum'\]",
            id="unknown-class-key",
        ),
        pytest.param(
            CLASS_RATES_2025.replace('  "8":\n', "  8:\n"),
            r"classes: key 8 must be a string, got int",
            id="class-number-as-yaml-number",
        ),
        pytest.param(
            CLASS_RATES_2025.replace('  "8":\n', '  "eight":\n'),
            r"classes.* is not a decimal: 'eight'",
            id="class-number-not-decimal",
        ),
        pytest.param(
            CLASS_RATES_2025.replace('  "8":\n', '  "0":\n'),
            "class_number must be positive",
            id="class-number-zero",
        ),
        pytest.param(
            CLASS_RATES_2025.replace('  "8":\n', '  "10.10":\n'),
            "class 10.1.? is listed more than once",
            id="class-number-twice-by-value",
        ),
        pytest.param(
            CLASS_RATES_2025.replace(
                'aiip_factor: {numerator: "3", denominator: "2"}',
                'aiip_factor: {numerator: "-3", denominator: "2"}',
            ),
            r"classes\.43\.1\.aiip_factor\.numerator is not a whole number: '-3'",
            id="factor-numerator-negative",
        ),
        pytest.param(
            CLASS_RATES_2025.replace(
                'riip_factor: {numerator: "7", denominator: "3"}',
                'riip_factor: {numerator: "7", denominator: "0"}',
            ),
            r"classes\.43\.1.*fraction denominator must be positive, got 0",
            id="factor-denominator-zero",
        ),
        pytest.param(
            CLASS_RATES_2025.replace(
                'riip_factor: {numerator: "7", denominator: "3"}',
                'riip_factor: {numerator: 7, denominator: "3"}',
            ),
            r"classes\.43\.1\.riip_factor\.numerator must be a string, got int",
            id="factor-numerator-as-yaml-number",
        ),
        pytest.param(
            CLASS_RATES_2025.replace(
                'riip_factor: {numerator: "7", denominator: "3"}',
                'riip_factor: {numerator: "7"}',
            ),
            r"classes\.43\.1\.riip_factor: missing keys \['denominator'\]",
            id="factor-denominator-missing",
        ),
        pytest.param(
            CLASS_RATES_2025.replace(
                'aiip_factor: {numerator: "3", denominator: "2"}', 'aiip_factor: "1.5"'
            ),
            r"classes\.43\.1\.aiip_factor must be a mapping",
            id="factor-as-a-decimal",
        ),
        pytest.param(
            CLASS_RATES_2025.split("classes:\n")[0] + "classes: {}\n",
            "at least one class",
            id="no-classes",
        ),
        pytest.param(
            CLASS_RATES_2025.split("classes:\n")[0] + 'classes:\n  - "8"\n',
            r"classes must be a mapping",
            id="classes-as-a-list",
        ),
        pytest.param(
            CLASS_RATES_2025.replace("classes:", "rows:"),
            r"unknown keys \['rows'\]",
            id="rows-are-not-classes",
        ),
        pytest.param(
            CLASS_RATES_2025.replace("kind: class_rates", "kind: rate_table"),
            "kind 'rate_table' does not match the requested 'class_rates'",
            id="kind-mismatch",
        ),
        pytest.param(
            CLASS_RATES_2025.replace("rounding: none\n", ""),
            r"missing keys \['rounding'\]",
            id="rounding-missing",
        ),
        pytest.param(
            CLASS_RATES_2025.replace('full_year_days: "365"\n', ""),
            r"missing keys \['full_year_days'\]",
            id="full-year-days-missing",
        ),
        pytest.param(
            CLASS_RATES_2025.replace('full_year_days: "365"', "full_year_days: 365"),
            "full_year_days must be a string, got int",
            id="full-year-days-as-yaml-number",
        ),
        pytest.param(
            CLASS_RATES_2025.replace('full_year_days: "365"', 'full_year_days: "a year"'),
            "full_year_days is not a whole number: 'a year'",
            id="full-year-days-not-a-whole-number",
        ),
        pytest.param(
            CLASS_RATES_2025.replace('full_year_days: "365"', 'full_year_days: "365.5"'),
            "full_year_days is not a whole number: '365.5'",
            id="full-year-days-fractional",
        ),
        pytest.param(
            CLASS_RATES_2025.replace('full_year_days: "365"', 'full_year_days: "0"'),
            "full_year_days must be positive, got 0",
            id="full-year-days-zero",
        ),
        pytest.param(
            CLASS_RATES_2025.replace(
                "sources:\n  - https://example.org/class-rates-2025", "sources: []"
            ),
            "sources must list at least one",
            id="sources-empty",
        ),
    ],
)
def test_rejects_malformed_class_rates_dataset(tmp_path: Path, content: str, message: str) -> None:
    write(tmp_path, "ex/parameters/class_rates/2025.yaml", content)

    with pytest.raises(InvalidParameterDataError, match=message) as excinfo:
        source(tmp_path).get("ex/class_rates", 2025, CLASS_RATES)

    assert "2025.yaml" in str(excinfo.value)


# A class may list `elections`, a mapping keyed by each code as a quoted whole number above 0, each
# a quoted decimal `rate` between 0 and 1: the rate a row takes when the caller elects that code
# (Guide T4036 2025, "Class 1 (4%)"). A class that does not list it has none.

ELECTIONS = (
    "    elections:\n"
    '      "1": {rate: "0.10"}\n'
    '      "2":\n'
    '        rate: "0.06"\n'
    '      "3": {rate: "0.10"}\n'
)


CLASS_RATES_WITH_ELECTIONS = CLASS_RATES_2025.replace('  "10.1":\n', '  "10.1":\n' + ELECTIONS, 1)


def test_reads_the_elections_of_a_class_in_the_files_order(tmp_path: Path) -> None:
    write(tmp_path, "ex/parameters/class_rates/2025.yaml", CLASS_RATES_WITH_ELECTIONS)

    table = source(tmp_path).get("ex/class_rates", 2025, CLASS_RATES).values

    held = table.for_class(D("10.1"))
    assert held is not None
    assert held.elections == (
        ClassElection(1, Rate(D("0.10"))),
        ClassElection(2, Rate(D("0.06"))),
        ClassElection(3, Rate(D("0.10"))),
    )
    assert [str(election.rate.value) for election in held.elections] == ["0.10", "0.06", "0.10"]
    assert held.election_rate(2) == Rate(D("0.06"))
    assert held.election_rate(4) is None


def test_a_class_without_elections_has_none(tmp_path: Path) -> None:
    write(tmp_path, "ex/parameters/class_rates/2025.yaml", CLASS_RATES_WITH_ELECTIONS)

    table = source(tmp_path).get("ex/class_rates", 2025, CLASS_RATES).values

    assert table.classes[0] == CLASS_RATES_CLASSES[0]
    assert table.classes[2] == CLASS_RATES_CLASSES[2]
    assert table.classes[3] == CLASS_RATES_CLASSES[3]


def test_a_dataset_without_elections_reads_as_before(tmp_path: Path) -> None:
    write(tmp_path, "ex/parameters/class_rates/2025.yaml", CLASS_RATES_2025)

    table = source(tmp_path).get("ex/class_rates", 2025, CLASS_RATES).values

    assert all(each.elections == () for each in table.classes)
    assert table.classes == CLASS_RATES_CLASSES


@pytest.mark.parametrize(
    ("old", "new", "message"),
    [
        pytest.param(
            '"1": {rate: "0.10"}',
            '1: {rate: "0.10"}',
            r"classes\.10\.1\.elections: key 1 must be a string, got int",
            id="code-as-yaml-number",
        ),
        pytest.param(
            '"1": {rate: "0.10"}',
            '"one": {rate: "0.10"}',
            r"classes\.10\.1\.elections.* is not a whole number: 'one'",
            id="code-not-a-whole-number",
        ),
        pytest.param(
            '"1": {rate: "0.10"}',
            '"1.5": {rate: "0.10"}',
            r"classes\.10\.1\.elections.* is not a whole number: '1.5'",
            id="code-fractional",
        ),
        pytest.param(
            '"1": {rate: "0.10"}',
            '"0": {rate: "0.10"}',
            r"classes\.10\.1.*code must be above 0",
            id="code-zero",
        ),
        pytest.param(
            '"1": {rate: "0.10"}',
            '"1": {rate: 0.10}',
            r"classes\.10\.1\.elections\.1\.rate must be a string, got float",
            id="rate-as-yaml-number",
        ),
        pytest.param(
            '"1": {rate: "0.10"}',
            '"1": {rate: "1.5"}',
            "rate must be between 0 and 1",
            id="rate-above-one",
        ),
        pytest.param(
            '"1": {rate: "0.10"}',
            '"1": {rate: "ten"}',
            r"classes\.10\.1\.elections\.1\.rate is not a decimal: 'ten'",
            id="rate-not-decimal",
        ),
        pytest.param(
            '"1": {rate: "0.10"}',
            '"1": {}',
            r"classes\.10\.1\.elections\.1: missing keys \['rate'\]",
            id="rate-missing",
        ),
        pytest.param(
            '"1": {rate: "0.10"}',
            '"1": {rate: "0.10", label: "rental"}',
            r"classes\.10\.1\.elections\.1: unknown keys \['label'\]",
            id="unknown-election-key",
        ),
        pytest.param(
            ELECTIONS,
            '    elections:\n      - {rate: "0.10"}\n',
            r"classes\.10\.1\.elections must be a mapping",
            id="elections-as-a-list",
        ),
    ],
)
def test_rejects_malformed_class_elections(
    tmp_path: Path, old: str, new: str, message: str
) -> None:
    content = CLASS_RATES_WITH_ELECTIONS.replace(old, new, 1)
    write(tmp_path, "ex/parameters/class_rates/2025.yaml", content)

    with pytest.raises(InvalidParameterDataError, match=message) as excinfo:
        source(tmp_path).get("ex/class_rates", 2025, CLASS_RATES)

    assert "2025.yaml" in str(excinfo.value)


def test_a_duplicate_class_error_is_not_attributed_to_the_full_year_days(tmp_path: Path) -> None:
    content = CLASS_RATES_2025.replace('  "8":\n', '  "10.10":\n')
    write(tmp_path, "ex/parameters/class_rates/2025.yaml", content)

    with pytest.raises(InvalidParameterDataError) as excinfo:
        source(tmp_path).get("ex/class_rates", 2025, CLASS_RATES)

    assert "listed more than once" in str(excinfo.value)
    assert "full_year_days" not in str(excinfo.value)


@pytest.mark.parametrize(
    ("old", "new"),
    [
        ('full_year_days: "365"', 'full_year_days: "0"'),
        ('  "8":\n', '  "0":\n'),
        ('  "8":\n', '  "10.10":\n'),
        ('denominator: "3"}', 'denominator: "0"}'),
    ],
)
def test_an_invalid_class_rates_table_is_reported_as_a_class_rates_error(
    tmp_path: Path, old: str, new: str
) -> None:
    write(tmp_path, "ex/parameters/class_rates/2025.yaml", CLASS_RATES_2025.replace(old, new))

    with pytest.raises(InvalidParameterDataError) as excinfo:
        source(tmp_path).get("ex/class_rates", 2025, CLASS_RATES)

    assert isinstance(excinfo.value.__cause__, InvalidClassRatesError)


@pytest.mark.parametrize("factor", ["aiip_factor", "riip_factor"])
def test_a_zero_factor_denominator_is_fractions_own_error_named_by_its_class(
    tmp_path: Path, factor: str
) -> None:
    # As a rate table names the row of a refused rate, the table names the class of a refused
    # factor; the refusal itself is the `fraction` kind's.
    old = {
        "aiip_factor": 'aiip_factor: {numerator: "3", denominator: "2"}',
        "riip_factor": 'riip_factor: {numerator: "7", denominator: "3"}',
    }[factor]
    new = old.replace('denominator: "2"', 'denominator: "0"').replace(
        'denominator: "3"', 'denominator: "0"'
    )
    write(tmp_path, "ex/parameters/class_rates/2025.yaml", CLASS_RATES_2025.replace(old, new))

    with pytest.raises(
        InvalidParameterDataError,
        match=r"classes\.43\.1.*fraction denominator must be positive, got 0",
    ) as excinfo:
        source(tmp_path).get("ex/class_rates", 2025, CLASS_RATES)

    assert isinstance(excinfo.value.__cause__, InvalidClassRatesError)
    assert isinstance(excinfo.value.__cause__.__cause__, InvalidFractionError)


def test_a_rate_table_dataset_is_not_a_class_rates_dataset(tmp_path: Path) -> None:
    write(tmp_path, "ex/parameters/rate_table/2025.yaml", RATE_TABLE_2025)

    with pytest.raises(InvalidParameterDataError, match="kind 'rate_table' does not match"):
        source(tmp_path).get("ex/rate_table", 2025, CLASS_RATES)


def test_a_class_rates_dataset_is_not_a_rate_table_dataset(tmp_path: Path) -> None:
    write(tmp_path, "ex/parameters/class_rates/2025.yaml", CLASS_RATES_2025)

    with pytest.raises(InvalidParameterDataError, match="kind 'class_rates' does not match"):
        source(tmp_path).get("ex/class_rates", 2025, RATE_TABLE)


#
# A `rounding_only` dataset is the shared envelope alone: its `rounding` rule is all it carries.


def test_reads_a_rounding_only_dataset(tmp_path: Path) -> None:
    write(tmp_path, "ex/parameters/rounding_only/2025.yaml", ROUNDING_ONLY_2025)

    result = source(tmp_path).get("ex/rounding_only", 2025, ROUNDING_ONLY)

    assert result == ParameterDataset(
        family="ex/rounding_only",
        tax_year=2025,
        kind=ROUNDING_ONLY,
        values=RoundingOnly(),
        rounding=RoundTo(D("0.01"), RoundingMode.HALF_UP),
        sources=("https://example.org/rounding-only-2025",),
    )


def test_reads_a_rounding_only_dataset_without_rounding(tmp_path: Path) -> None:
    write(
        tmp_path,
        "ex/parameters/rounding_only/2025.yaml",
        ROUNDING_ONLY_2025.replace(
            'rounding: {increment: "0.01", mode: half_up}', "rounding: none"
        ),
    )

    result = source(tmp_path).get("ex/rounding_only", 2025, ROUNDING_ONLY)

    assert result.rounding == NO_ROUNDING
    assert result.values == RoundingOnly()


def test_by_default_the_rounding_only_parser_comes_from_the_shared_registry(
    tmp_path: Path,
) -> None:
    write(tmp_path, "ex/parameters/rounding_only/2025.yaml", ROUNDING_ONLY_2025)

    result = YamlParameterSource(roots(tmp_path), built_in_parsers()).get(
        "ex/rounding_only", 2025, ROUNDING_ONLY
    )

    assert result.values == RoundingOnly()


@pytest.mark.parametrize(
    ("content", "message"),
    [
        pytest.param(
            ROUNDING_ONLY_2025 + 'rate: "0.5"\n',
            r"unknown keys \['rate'\]",
            id="rate-is-not-a-rounding-only-key",
        ),
        pytest.param(
            ROUNDING_ONLY_2025 + 'amount: "100"\n',
            r"unknown keys \['amount'\]",
            id="amount-is-not-a-rounding-only-key",
        ),
        pytest.param(
            ROUNDING_ONLY_2025.replace('rounding: {increment: "0.01", mode: half_up}\n', ""),
            r"missing keys \['rounding'\]",
            id="rounding-missing",
        ),
        pytest.param(
            ROUNDING_ONLY_2025.replace("kind: rounding_only", "kind: rate"),
            "kind 'rate' does not match the requested 'rounding_only'",
            id="kind-mismatch",
        ),
        pytest.param(
            ROUNDING_ONLY_2025.replace(
                "sources:\n  - https://example.org/rounding-only-2025", "sources: []"
            ),
            "sources must list at least one",
            id="sources-empty",
        ),
    ],
)
def test_rejects_malformed_rounding_only_dataset(
    tmp_path: Path, content: str, message: str
) -> None:
    write(tmp_path, "ex/parameters/rounding_only/2025.yaml", content)

    with pytest.raises(InvalidParameterDataError, match=message) as excinfo:
        source(tmp_path).get("ex/rounding_only", 2025, ROUNDING_ONLY)

    assert "2025.yaml" in str(excinfo.value)


def test_a_rate_dataset_is_not_a_rounding_only_dataset(tmp_path: Path) -> None:
    write(tmp_path, "ex/parameters/credit_rate/2025.yaml", RATE_2025)

    with pytest.raises(InvalidParameterDataError, match="kind 'rate' does not match"):
        source(tmp_path).get("ex/credit_rate", 2025, ROUNDING_ONLY)


#
# A `conditions` dataset holds `count_when_any_applies` (a quoted whole number, "0" or "1") and
# `conditions`, a list in the form's order, each a `text` and `parts`; each part holds `tests`;
# each test a `reads`, a `position` (quoted, from 1), a `relation` and exactly one of `than` (a
# quoted decimal) and `against` (a quoted position, from 1).

FIRST_TEST = '          - {reads: count, position: "1", relation: equal_to, than: "1"}\n'


FIRST_PARTS = "    parts:\n      - tests:\n" + FIRST_TEST


CONDITIONS_VALUES = ConditionList(
    0,
    (
        Condition(
            "You were bankrupt at any time in 2025",
            (ConditionPart((ConditionTest("count", 1, "equal_to", D("1"), None),)),),
        ),
        Condition(
            "There is an amount on line 72",
            (ConditionPart((ConditionTest("amount", 1, "not_equal_to", D("0"), None),)),),
        ),
        Condition(
            "You entered an amount and the other amount is more than $82,125.50",
            (
                ConditionPart(
                    (
                        ConditionTest("count", 2, "not_equal_to", D("0"), None),
                        ConditionTest("amount", 2, "not_equal_to", D("0"), None),
                    )
                ),
                ConditionPart((ConditionTest("amount", 3, "more_than", D("82125.50"), None),)),
            ),
        ),
        Condition(
            "The first amount is more than the second",
            (ConditionPart((ConditionTest("amount", 1, "more_than", None, 2),)),),
        ),
    ),
)


def test_reads_a_conditions_dataset(tmp_path: Path) -> None:
    write(tmp_path, "ex/parameters/conditions/2025.yaml", CONDITIONS_2025)

    result = source(tmp_path).get("ex/conditions", 2025, CONDITIONS)

    assert result == ParameterDataset(
        family="ex/conditions",
        tax_year=2025,
        kind=CONDITIONS,
        values=CONDITIONS_VALUES,
        rounding=NO_ROUNDING,
        sources=("https://example.org/conditions-2025",),
    )


def test_reads_the_conditions_in_the_order_written(tmp_path: Path) -> None:
    write(tmp_path, "ex/parameters/conditions/2025.yaml", CONDITIONS_2025)

    listed = source(tmp_path).get("ex/conditions", 2025, CONDITIONS).values

    assert [entry.text for entry in listed.conditions] == [
        "You were bankrupt at any time in 2025",
        "There is an amount on line 72",
        "You entered an amount and the other amount is more than $82,125.50",
        "The first amount is more than the second",
    ]


def test_reads_a_conditions_figures_exactly(tmp_path: Path) -> None:
    write(tmp_path, "ex/parameters/conditions/2025.yaml", CONDITIONS_2025)

    listed = source(tmp_path).get("ex/conditions", 2025, CONDITIONS).values

    third = listed.conditions[2].parts[1].tests[0]
    assert third.than is not None
    assert str(third.than) == "82125.50"


def test_reads_one_as_the_count_when_any_applies(tmp_path: Path) -> None:
    content = CONDITIONS_2025.replace('count_when_any_applies: "0"', 'count_when_any_applies: "1"')
    write(tmp_path, "ex/parameters/conditions/2025.yaml", content)

    listed = source(tmp_path).get("ex/conditions", 2025, CONDITIONS).values

    assert listed.count_when_any_applies == 1


def test_reads_a_conditions_dataset_written_as_block_mappings(tmp_path: Path) -> None:
    content = CONDITIONS_2025.replace(
        '          - {reads: count, position: "1", relation: equal_to, than: "1"}\n',
        '          - reads: count\n            position: "1"\n            relation: equal_to\n'
        '            than: "1"\n',
    )
    write(tmp_path, "ex/parameters/conditions/2025.yaml", content)

    assert source(tmp_path).get("ex/conditions", 2025, CONDITIONS).values == CONDITIONS_VALUES


def test_reads_a_conditions_datasets_rounding_rule(tmp_path: Path) -> None:
    write(
        tmp_path,
        "ex/parameters/conditions/2025.yaml",
        CONDITIONS_2025.replace("rounding: none", 'rounding: {increment: "0.01", mode: half_up}'),
    )

    result = source(tmp_path).get("ex/conditions", 2025, CONDITIONS)

    assert result.rounding == RoundTo(D("0.01"), RoundingMode.HALF_UP)


def test_by_default_the_conditions_parser_comes_from_the_shared_registry(tmp_path: Path) -> None:
    write(tmp_path, "ex/parameters/conditions/2025.yaml", CONDITIONS_2025)

    result = YamlParameterSource(roots(tmp_path), built_in_parsers()).get(
        "ex/conditions", 2025, CONDITIONS
    )

    assert result.values == CONDITIONS_VALUES


@pytest.mark.parametrize(
    ("content", "message"),
    [
        pytest.param(
            CONDITIONS_2025.replace('count_when_any_applies: "0"', "count_when_any_applies: 0"),
            "count_when_any_applies must be a string, got int",
            id="count-as-yaml-number",
        ),
        pytest.param(
            CONDITIONS_2025.replace('count_when_any_applies: "0"', 'count_when_any_applies: "two"'),
            "count_when_any_applies is not a whole number: 'two'",
            id="count-not-a-number",
        ),
        pytest.param(
            CONDITIONS_2025.replace('count_when_any_applies: "0"', 'count_when_any_applies: "2"'),
            "count_when_any_applies must be 0 or 1",
            id="count-not-0-or-1",
        ),
        pytest.param(
            CONDITIONS_2025.replace('count_when_any_applies: "0"\n', ""),
            r"missing keys \['count_when_any_applies'\]",
            id="count-missing",
        ),
        pytest.param(
            CONDITIONS_2025.split("conditions:\n")[0] + "conditions: []\n",
            "at least one condition",
            id="no-conditions",
        ),
        pytest.param(
            CONDITIONS_2025.replace("conditions:\n", "rules:\n"),
            r"unknown keys \['rules'\]",
            id="rules-are-not-conditions",
        ),
        pytest.param(
            CONDITIONS_2025.replace(
                "  - text: You were bankrupt at any time in 2025\n"
                "    parts:\n"
                "      - tests:\n"
                '          - {reads: count, position: "1", relation: equal_to, than: "1"}\n',
                "  - not a condition\n",
            ),
            r"conditions\[0\] must be a mapping",
            id="condition-not-a-mapping",
        ),
        pytest.param(
            CONDITIONS_2025.replace(
                "  - text: You were bankrupt at any time in 2025\n    parts", "  - parts"
            ),
            r"conditions\[0\]: missing keys \['text'\]",
            id="text-missing",
        ),
        pytest.param(
            CONDITIONS_2025.replace("text: You were bankrupt at any time in 2025", 'text: ""'),
            "text must not be empty",
            id="text-empty",
        ),
        pytest.param(
            CONDITIONS_2025.replace(
                FIRST_PARTS,
                "",
            ),
            r"conditions\[0\]: missing keys \['parts'\]",
            id="parts-missing",
        ),
        pytest.param(
            CONDITIONS_2025.replace(
                FIRST_PARTS,
                "    parts: []\n",
            ),
            "at least one part",
            id="parts-empty",
        ),
        pytest.param(
            CONDITIONS_2025.replace(
                "      - tests:\n" + FIRST_TEST,
                "      - {}\n",
            ),
            r"conditions\[0\].parts\[0\]: missing keys \['tests'\]",
            id="tests-missing",
        ),
        pytest.param(
            CONDITIONS_2025.replace(
                "      - tests:\n" + FIRST_TEST,
                "      - tests: []\n",
            ),
            "at least one test",
            id="tests-empty",
        ),
        pytest.param(
            CONDITIONS_2025.replace('reads: count, position: "1"', 'reads: money, position: "1"'),
            r"conditions\[0\].*reads must be 'count' or 'amount'",
            id="reads-unknown",
        ),
        pytest.param(
            CONDITIONS_2025.replace("relation: equal_to", "relation: less_than"),
            r"conditions\[0\].*relation must be 'equal_to', 'not_equal_to' or 'more_than'",
            id="relation-unknown",
        ),
        pytest.param(
            CONDITIONS_2025.replace(
                'reads: count, position: "1", relation: equal_to, than: "1"',
                'reads: count, position: "1", relation: equal_to',
            ),
            r"conditions\[0\].*exactly one of than and against",
            id="neither-than-nor-against",
        ),
        pytest.param(
            CONDITIONS_2025.replace(
                'relation: more_than, against: "2"',
                'relation: more_than, against: "2", than: "5"',
            ),
            "exactly one of than and against",
            id="both-than-and-against",
        ),
        pytest.param(
            CONDITIONS_2025.replace('against: "2"', "against: 2"),
            "against must be a string, got int",
            id="against-as-yaml-number",
        ),
        pytest.param(
            CONDITIONS_2025.replace('against: "2"', 'against: "0"'),
            "against must be 1 or more",
            id="against-below-1",
        ),
        pytest.param(
            CONDITIONS_2025.replace('against: "2"', 'against: "two"'),
            "against is not a whole number: 'two'",
            id="against-not-a-number",
        ),
        pytest.param(
            CONDITIONS_2025.replace(
                '{reads: count, position: "1", relation: equal_to, than: "1"}',
                '{reads: count, position: "1", relation: equal_to, against: "2"}',
            ),
            "against needs reads 'amount'",
            id="against-on-a-count",
        ),
        pytest.param(
            CONDITIONS_2025.replace(
                'reads: count, position: "1", relation', "reads: count, relation"
            ),
            r"tests\[0\]: missing keys \['position'\]",
            id="position-missing",
        ),
        pytest.param(
            CONDITIONS_2025.replace(
                'position: "1", relation: equal_to', "position: 1, relation: equal_to"
            ),
            r"tests\[0\].position must be a string, got int",
            id="position-as-yaml-number",
        ),
        pytest.param(
            CONDITIONS_2025.replace(
                'position: "1", relation: equal_to', 'position: "0", relation: equal_to'
            ),
            "position must be 1 or more",
            id="position-below-1",
        ),
        pytest.param(
            CONDITIONS_2025.replace(
                'position: "1", relation: equal_to', 'position: "first", relation: equal_to'
            ),
            r"tests\[0\].position is not a whole number: 'first'",
            id="position-not-a-number",
        ),
        pytest.param(
            CONDITIONS_2025.replace('than: "1"', "than: 1"),
            r"conditions\[0\].parts\[0\].tests\[0\].than must be a string, got int",
            id="than-as-yaml-number",
        ),
        pytest.param(
            CONDITIONS_2025.replace('than: "1"', 'than: "lots"'),
            r"tests\[0\].than is not a decimal: 'lots'",
            id="than-not-decimal",
        ),
        pytest.param(
            CONDITIONS_2025.replace("relation: equal_to,", 'relation: equal_to, threshold: "1",'),
            r"tests\[0\]: unknown keys \['threshold'\]",
            id="unknown-test-key",
        ),
        pytest.param(
            CONDITIONS_2025.replace("kind: conditions", "kind: rate"),
            "kind 'rate' does not match the requested 'conditions'",
            id="kind-mismatch",
        ),
        pytest.param(
            CONDITIONS_2025.replace("rounding: none\n", ""),
            r"missing keys \['rounding'\]",
            id="rounding-missing",
        ),
        pytest.param(
            CONDITIONS_2025.replace(
                "sources:\n  - https://example.org/conditions-2025", "sources: []"
            ),
            "sources must list at least one",
            id="sources-empty",
        ),
    ],
)
def test_rejects_malformed_conditions_dataset(tmp_path: Path, content: str, message: str) -> None:
    write(tmp_path, "ex/parameters/conditions/2025.yaml", content)

    with pytest.raises(InvalidParameterDataError, match=message) as excinfo:
        source(tmp_path).get("ex/conditions", 2025, CONDITIONS)

    assert "2025.yaml" in str(excinfo.value)


@pytest.mark.parametrize(
    ("old", "new"),
    [
        ('count_when_any_applies: "0"', 'count_when_any_applies: "2"'),
        ('reads: count, position: "1"', 'reads: money, position: "1"'),
        ("relation: equal_to", "relation: less_than"),
        ('against: "2"', 'against: "0"'),
        ('position: "1", relation: equal_to', 'position: "0", relation: equal_to'),
    ],
)
def test_an_invalid_conditions_dataset_is_reported_as_a_conditions_error(
    tmp_path: Path, old: str, new: str
) -> None:
    write(tmp_path, "ex/parameters/conditions/2025.yaml", CONDITIONS_2025.replace(old, new))

    with pytest.raises(InvalidParameterDataError) as excinfo:
        source(tmp_path).get("ex/conditions", 2025, CONDITIONS)

    assert isinstance(excinfo.value.__cause__, InvalidConditionsError)


def test_an_empty_list_of_conditions_is_reported_as_a_conditions_error(tmp_path: Path) -> None:
    content = CONDITIONS_2025.split("conditions:\n")[0] + "conditions: []\n"
    write(tmp_path, "ex/parameters/conditions/2025.yaml", content)

    with pytest.raises(InvalidParameterDataError) as excinfo:
        source(tmp_path).get("ex/conditions", 2025, CONDITIONS)

    assert isinstance(excinfo.value.__cause__, InvalidConditionsError)


def test_a_rate_table_dataset_is_not_a_conditions_dataset(tmp_path: Path) -> None:
    write(tmp_path, "ex/parameters/rate_table/2025.yaml", RATE_TABLE_2025)

    with pytest.raises(InvalidParameterDataError, match="kind 'rate_table' does not match"):
        source(tmp_path).get("ex/rate_table", 2025, CONDITIONS)


def test_a_conditions_dataset_is_not_a_rate_table_dataset(tmp_path: Path) -> None:
    write(tmp_path, "ex/parameters/conditions/2025.yaml", CONDITIONS_2025)

    with pytest.raises(InvalidParameterDataError, match="kind 'conditions' does not match"):
        source(tmp_path).get("ex/conditions", 2025, RATE_TABLE)
