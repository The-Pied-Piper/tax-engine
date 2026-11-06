"""Unit tests for reading the Canada-only parameter kinds through YamlParameterSource.

Amount by count, claim reduction, contribution tier, taper and year amounts. Values are made up.
"""

from __future__ import annotations

from decimal import Decimal
from pathlib import Path

import pytest

from tax_engine.adapters.outbound.yaml_parameters import YamlParameterSource
from tax_engine.domain.errors import (
    InvalidAmountByCountError,
    InvalidClaimReductionError,
    InvalidContributionTierError,
    InvalidParameterDataError,
    InvalidRateError,
    InvalidTaperError,
    InvalidYearAmountsError,
)
from tax_engine.domain.parameters.amount import AMOUNT
from tax_engine.domain.parameters.credit import CREDIT
from tax_engine.domain.parameters.datasets import ParameterDataset
from tax_engine.domain.parameters.rate import RATE, Rate
from tax_engine.domain.parameters.rounding import NO_ROUNDING, RoundingMode, RoundTo
from tax_engine.jurisdictions.ca.parameter_shapes.amount_by_count import (
    AMOUNT_BY_COUNT,
    AmountByCount,
)
from tax_engine.jurisdictions.ca.parameter_shapes.claim_reduction import (
    CLAIM_REDUCTION,
    ClaimReduction,
)
from tax_engine.jurisdictions.ca.parameter_shapes.contribution_tier import (
    CONTRIBUTION_TIER,
    ContributionTier,
)
from tax_engine.jurisdictions.ca.parameter_shapes.taper import TAPER, Taper
from tax_engine.jurisdictions.ca.parameter_shapes.year_amounts import (
    YEAR_AMOUNTS,
    YearAmounts,
    YearAmountsRow,
)
from tests.parameter_source_support import (
    AMOUNT_2025,
    RATE_2025,
    D,
    roots,
    write,
)
from tests.parameter_source_support import (
    ca_parsers as built_in_parsers,
)


def source(directory: Path) -> YamlParameterSource:
    return YamlParameterSource(roots(directory), parsers=built_in_parsers())


CLAIM_REDUCTION_2025 = """\
family: ex/claim_reduction
tax_year: 2025
kind: claim_reduction
sources:
  - https://example.org/claim-reduction-2025
rounding: none
rate: "0.03"
ceiling: "2834"
"""


CLAIM_REDUCTION_WITH_MAXIMUM_2025 = CLAIM_REDUCTION_2025 + 'maximum: "15551"\n'


YEAR_AMOUNTS_2025 = """\
family: ex/year_amounts
tax_year: 2025
kind: year_amounts
sources:
  - https://example.org/year-amounts-2025
rounding: none
rows:
  - from_year: 2024
    amounts: {interest_limit: "350", other_limit: "10.50"}
  - from_year: 2001
    amounts: {interest_limit: "300", other_limit: "9"}
  - amounts: {interest_limit: "250", other_limit: "8"}
"""


CONTRIBUTION_TIER_2025 = """\
family: ex/contribution_tier
tax_year: 2025
kind: contribution_tier
sources:
  - https://example.org/contribution-tier-2025
rounding: none
rate: "0.05"
lower: "3000"
upper: "50000"
maximum: "2350"
"""


TAPER_2025 = """\
family: ex/taper
tax_year: 2025
kind: taper
sources:
  - https://example.org/taper-2025
rounding: none
base: "1000"
supplement: "500"
threshold: "20000"
range: "10000"
"""


AMOUNT_BY_COUNT_2025 = """\
family: ex/amount_by_count
tax_year: 2025
kind: amount_by_count
sources:
  - https://example.org/amount-by-count-2025
rounding: none
amounts:
  "1": "100"
  "2": "200.50"
  "3": "300"
  "4": "400"
"""


def test_reads_a_contribution_tier_dataset(tmp_path: Path) -> None:
    write(tmp_path, "ex/parameters/contribution_tier/2025.yaml", CONTRIBUTION_TIER_2025)

    result = source(tmp_path).get("ex/contribution_tier", 2025, CONTRIBUTION_TIER)

    assert result == ParameterDataset(
        family="ex/contribution_tier",
        tax_year=2025,
        kind=CONTRIBUTION_TIER,
        values=ContributionTier(
            rate=Rate(D("0.05")), lower=D("3000"), upper=D("50000"), maximum=D("2350")
        ),
        rounding=NO_ROUNDING,
        sources=("https://example.org/contribution-tier-2025",),
    )


def test_reads_a_contribution_tiers_figures_exactly(tmp_path: Path) -> None:
    content = (
        CONTRIBUTION_TIER_2025.replace('rate: "0.05"', 'rate: "0.0495"')
        .replace('lower: "3000"', 'lower: "3000.50"')
        .replace('upper: "50000"', 'upper: "50000.00"')
        .replace('maximum: "2350"', 'maximum: "2350.10"')
    )
    write(tmp_path, "ex/parameters/contribution_tier/2025.yaml", content)

    tier = source(tmp_path).get("ex/contribution_tier", 2025, CONTRIBUTION_TIER).values

    assert (str(tier.rate.value), str(tier.lower), str(tier.upper), str(tier.maximum)) == (
        "0.0495",
        "3000.50",
        "50000.00",
        "2350.10",
    )


def test_reads_a_contribution_tier_starting_at_zero_with_a_zero_maximum(tmp_path: Path) -> None:
    content = CONTRIBUTION_TIER_2025.replace('lower: "3000"', 'lower: "0"').replace(
        'maximum: "2350"', 'maximum: "0"'
    )
    write(tmp_path, "ex/parameters/contribution_tier/2025.yaml", content)

    tier = source(tmp_path).get("ex/contribution_tier", 2025, CONTRIBUTION_TIER).values

    assert (tier.lower, tier.maximum) == (D("0"), D("0"))


def test_reads_a_contribution_tier_datasets_rounding_rule(tmp_path: Path) -> None:
    write(
        tmp_path,
        "ex/parameters/contribution_tier/2025.yaml",
        CONTRIBUTION_TIER_2025.replace(
            "rounding: none", 'rounding: {increment: "0.01", mode: half_up}'
        ),
    )

    result = source(tmp_path).get("ex/contribution_tier", 2025, CONTRIBUTION_TIER)

    assert result.rounding == RoundTo(D("0.01"), RoundingMode.HALF_UP)


def test_by_default_the_contribution_tier_parser_comes_from_the_shared_registry(
    tmp_path: Path,
) -> None:
    write(tmp_path, "ex/parameters/contribution_tier/2025.yaml", CONTRIBUTION_TIER_2025)

    result = YamlParameterSource(roots(tmp_path), built_in_parsers()).get(
        "ex/contribution_tier", 2025, CONTRIBUTION_TIER
    )

    assert result.values == ContributionTier(Rate(D("0.05")), D("3000"), D("50000"), D("2350"))


def test_reads_a_taper_dataset(tmp_path: Path) -> None:
    write(tmp_path, "ex/parameters/taper/2025.yaml", TAPER_2025)

    result = source(tmp_path).get("ex/taper", 2025, TAPER)

    assert result == ParameterDataset(
        family="ex/taper",
        tax_year=2025,
        kind=TAPER,
        values=Taper(base=D("1000"), supplement=D("500"), threshold=D("20000"), range=D("10000")),
        rounding=NO_ROUNDING,
        sources=("https://example.org/taper-2025",),
    )


def test_reads_a_tapers_figures_exactly(tmp_path: Path) -> None:
    content = (
        TAPER_2025.replace('base: "1000"', 'base: "1000.50"')
        .replace('supplement: "500"', 'supplement: "500.00"')
        .replace('threshold: "20000"', 'threshold: "20000.10"')
        .replace('range: "10000"', 'range: "10000.0"')
    )
    write(tmp_path, "ex/parameters/taper/2025.yaml", content)

    taper = source(tmp_path).get("ex/taper", 2025, TAPER).values

    assert (str(taper.base), str(taper.supplement), str(taper.threshold), str(taper.range)) == (
        "1000.50",
        "500.00",
        "20000.10",
        "10000.0",
    )


def test_reads_a_taper_with_a_zero_base_supplement_and_threshold(tmp_path: Path) -> None:
    content = (
        TAPER_2025.replace('base: "1000"', 'base: "0"')
        .replace('supplement: "500"', 'supplement: "0"')
        .replace('threshold: "20000"', 'threshold: "0"')
    )
    write(tmp_path, "ex/parameters/taper/2025.yaml", content)

    taper = source(tmp_path).get("ex/taper", 2025, TAPER).values

    assert (taper.base, taper.supplement, taper.threshold) == (D("0"), D("0"), D("0"))


def test_reads_a_taper_datasets_rounding_rule(tmp_path: Path) -> None:
    write(
        tmp_path,
        "ex/parameters/taper/2025.yaml",
        TAPER_2025.replace("rounding: none", 'rounding: {increment: "0.01", mode: half_up}'),
    )

    result = source(tmp_path).get("ex/taper", 2025, TAPER)

    assert result.rounding == RoundTo(D("0.01"), RoundingMode.HALF_UP)


def test_by_default_the_taper_parser_comes_from_the_shared_registry(tmp_path: Path) -> None:
    write(tmp_path, "ex/parameters/taper/2025.yaml", TAPER_2025)

    result = YamlParameterSource(roots(tmp_path), built_in_parsers()).get("ex/taper", 2025, TAPER)

    assert result.values == Taper(D("1000"), D("500"), D("20000"), D("10000"))


def test_reads_an_amount_by_count_dataset(tmp_path: Path) -> None:
    write(tmp_path, "ex/parameters/amount_by_count/2025.yaml", AMOUNT_BY_COUNT_2025)

    result = source(tmp_path).get("ex/amount_by_count", 2025, AMOUNT_BY_COUNT)

    assert result == ParameterDataset(
        family="ex/amount_by_count",
        tax_year=2025,
        kind=AMOUNT_BY_COUNT,
        values=AmountByCount(((1, D("100")), (2, D("200.50")), (3, D("300")), (4, D("400")))),
        rounding=NO_ROUNDING,
        sources=("https://example.org/amount-by-count-2025",),
    )


def test_reads_an_amount_by_counts_counts_as_ints_and_amounts_as_decimals(
    tmp_path: Path,
) -> None:
    write(tmp_path, "ex/parameters/amount_by_count/2025.yaml", AMOUNT_BY_COUNT_2025)

    table = source(tmp_path).get("ex/amount_by_count", 2025, AMOUNT_BY_COUNT).values

    assert sorted(table.rows) == [(1, D("100")), (2, D("200.50")), (3, D("300")), (4, D("400"))]
    for count, amount in table.rows:
        assert type(count) is int
        assert type(amount) is Decimal


def test_reads_an_amount_by_counts_amounts_exactly(tmp_path: Path) -> None:
    content = AMOUNT_BY_COUNT_2025.replace('"1": "100"', '"1": "100.10"').replace(
        '"2": "200.50"', '"2": "200.500"'
    )
    write(tmp_path, "ex/parameters/amount_by_count/2025.yaml", content)

    table = source(tmp_path).get("ex/amount_by_count", 2025, AMOUNT_BY_COUNT).values

    assert {count: str(amount) for count, amount in table.rows}[1] == "100.10"
    assert {count: str(amount) for count, amount in table.rows}[2] == "200.500"


def test_reads_an_amount_by_count_with_a_count_of_zero_and_a_zero_amount(tmp_path: Path) -> None:
    content = AMOUNT_BY_COUNT_2025.replace('"1": "100"', '"0": "0"')
    write(tmp_path, "ex/parameters/amount_by_count/2025.yaml", content)

    table = source(tmp_path).get("ex/amount_by_count", 2025, AMOUNT_BY_COUNT).values

    assert (0, D("0")) in table.rows


def test_reads_an_amount_by_count_with_a_single_row(tmp_path: Path) -> None:
    content = AMOUNT_BY_COUNT_2025.replace('  "2": "200.50"\n  "3": "300"\n  "4": "400"\n', "")
    write(tmp_path, "ex/parameters/amount_by_count/2025.yaml", content)

    table = source(tmp_path).get("ex/amount_by_count", 2025, AMOUNT_BY_COUNT).values

    assert table.rows == ((1, D("100")),)


def test_reads_an_amount_by_counts_multi_digit_counts(tmp_path: Path) -> None:
    content = AMOUNT_BY_COUNT_2025.replace('"4": "400"', '"12": "1200"')
    write(tmp_path, "ex/parameters/amount_by_count/2025.yaml", content)

    table = source(tmp_path).get("ex/amount_by_count", 2025, AMOUNT_BY_COUNT).values

    assert (12, D("1200")) in table.rows


def test_reads_an_amount_by_count_datasets_rounding_rule(tmp_path: Path) -> None:
    write(
        tmp_path,
        "ex/parameters/amount_by_count/2025.yaml",
        AMOUNT_BY_COUNT_2025.replace(
            "rounding: none", 'rounding: {increment: "0.01", mode: half_up}'
        ),
    )

    result = source(tmp_path).get("ex/amount_by_count", 2025, AMOUNT_BY_COUNT)

    assert result.rounding == RoundTo(D("0.01"), RoundingMode.HALF_UP)


def test_by_default_the_amount_by_count_parser_comes_from_the_shared_registry(
    tmp_path: Path,
) -> None:
    write(tmp_path, "ex/parameters/amount_by_count/2025.yaml", AMOUNT_BY_COUNT_2025)

    result = YamlParameterSource(roots(tmp_path), built_in_parsers()).get(
        "ex/amount_by_count", 2025, AMOUNT_BY_COUNT
    )

    assert sorted(result.values.rows) == [
        (1, D("100")),
        (2, D("200.50")),
        (3, D("300")),
        (4, D("400")),
    ]


def test_reads_a_claim_reduction_dataset_without_a_maximum(tmp_path: Path) -> None:
    write(tmp_path, "ex/parameters/claim_reduction/2025.yaml", CLAIM_REDUCTION_2025)

    result = source(tmp_path).get("ex/claim_reduction", 2025, CLAIM_REDUCTION)

    assert result == ParameterDataset(
        family="ex/claim_reduction",
        tax_year=2025,
        kind=CLAIM_REDUCTION,
        values=ClaimReduction(Rate(D("0.03")), D("2834"), None),
        rounding=NO_ROUNDING,
        sources=("https://example.org/claim-reduction-2025",),
    )
    assert result.values.maximum is None


def test_reads_a_claim_reduction_dataset_with_a_maximum(tmp_path: Path) -> None:
    write(tmp_path, "ex/parameters/claim_reduction/2025.yaml", CLAIM_REDUCTION_WITH_MAXIMUM_2025)

    values = source(tmp_path).get("ex/claim_reduction", 2025, CLAIM_REDUCTION).values

    assert values == ClaimReduction(Rate(D("0.03")), D("2834"), D("15551"))


def test_reads_a_claim_reductions_figures_exactly(tmp_path: Path) -> None:
    content = (
        CLAIM_REDUCTION_WITH_MAXIMUM_2025.replace('rate: "0.03"', 'rate: "0.0305"')
        .replace('ceiling: "2834"', 'ceiling: "2834.50"')
        .replace('maximum: "15551"', 'maximum: "15551.10"')
    )
    write(tmp_path, "ex/parameters/claim_reduction/2025.yaml", content)

    values = source(tmp_path).get("ex/claim_reduction", 2025, CLAIM_REDUCTION).values

    assert str(values.rate.value) == "0.0305"
    assert str(values.ceiling) == "2834.50"
    assert str(values.maximum) == "15551.10"  # exact, scale kept


def test_reads_a_claim_reduction_datasets_rounding_rule(tmp_path: Path) -> None:
    write(
        tmp_path,
        "ex/parameters/claim_reduction/2025.yaml",
        CLAIM_REDUCTION_2025.replace(
            "rounding: none", 'rounding: {increment: "0.01", mode: half_up}'
        ),
    )

    result = source(tmp_path).get("ex/claim_reduction", 2025, CLAIM_REDUCTION)

    assert result.rounding == RoundTo(D("0.01"), RoundingMode.HALF_UP)


def test_by_default_the_claim_reduction_parser_comes_from_the_shared_registry(
    tmp_path: Path,
) -> None:
    write(tmp_path, "ex/parameters/claim_reduction/2025.yaml", CLAIM_REDUCTION_WITH_MAXIMUM_2025)

    result = YamlParameterSource(roots(tmp_path), built_in_parsers()).get(
        "ex/claim_reduction", 2025, CLAIM_REDUCTION
    )

    assert result.values == ClaimReduction(Rate(D("0.03")), D("2834"), D("15551"))


def test_a_claim_reduction_dataset_is_not_a_rate_dataset(tmp_path: Path) -> None:
    write(tmp_path, "ex/parameters/claim_reduction/2025.yaml", CLAIM_REDUCTION_2025)

    with pytest.raises(InvalidParameterDataError, match="kind 'claim_reduction' does not match"):
        source(tmp_path).get("ex/claim_reduction", 2025, RATE)


@pytest.mark.parametrize(
    ("content", "message"),
    [
        pytest.param(
            CLAIM_REDUCTION_2025.replace('rate: "0.03"', 'rate: "1.5"'),
            "rate must be between 0 and 1",
            id="rate-above-one",
        ),
        pytest.param(
            CLAIM_REDUCTION_2025.replace('rate: "0.03"', "rate: 0.03"),
            "rate must be a string, got float",
            id="rate-as-yaml-number",
        ),
        pytest.param(
            CLAIM_REDUCTION_2025.replace('ceiling: "2834"', "ceiling: 2834"),
            "ceiling must be a string, got int",
            id="ceiling-as-yaml-number",
        ),
        pytest.param(
            CLAIM_REDUCTION_2025.replace('ceiling: "2834"', 'ceiling: "lots"'),
            "ceiling is not a decimal: 'lots'",
            id="ceiling-not-decimal",
        ),
        pytest.param(
            CLAIM_REDUCTION_2025.replace('ceiling: "2834"', 'ceiling: "-1"'),
            "ceiling must not be negative",
            id="ceiling-negative",
        ),
        pytest.param(
            CLAIM_REDUCTION_2025.replace('ceiling: "2834"', 'ceiling: "Infinity"'),
            "ceiling is not a decimal",
            id="ceiling-infinite",
        ),
        pytest.param(
            CLAIM_REDUCTION_WITH_MAXIMUM_2025.replace('maximum: "15551"', "maximum: 15551"),
            "maximum must be a string, got int",
            id="maximum-as-yaml-number",
        ),
        pytest.param(
            CLAIM_REDUCTION_WITH_MAXIMUM_2025.replace('maximum: "15551"', 'maximum: "-1"'),
            "maximum must not be negative",
            id="maximum-negative",
        ),
        pytest.param(
            CLAIM_REDUCTION_WITH_MAXIMUM_2025.replace('maximum: "15551"', 'maximum: "lots"'),
            "maximum is not a decimal: 'lots'",
            id="maximum-not-decimal",
        ),
        pytest.param(
            CLAIM_REDUCTION_2025.replace('rate: "0.03"\n', ""),
            r"missing keys \['rate'\]",
            id="rate-missing",
        ),
        pytest.param(
            CLAIM_REDUCTION_2025.replace('ceiling: "2834"\n', ""),
            r"missing keys \['ceiling'\]",
            id="ceiling-missing",
        ),
        pytest.param(
            CLAIM_REDUCTION_2025 + 'amount: "1"\n',
            r"unknown keys \['amount'\]",
            id="unknown-key",
        ),
    ],
)
def test_rejects_an_invalid_claim_reduction_dataset(
    tmp_path: Path, content: str, message: str
) -> None:
    write(tmp_path, "ex/parameters/claim_reduction/2025.yaml", content)

    with pytest.raises(InvalidParameterDataError, match=message):
        source(tmp_path).get("ex/claim_reduction", 2025, CLAIM_REDUCTION)


def test_an_invalid_claim_reduction_figure_is_reported_as_a_claim_reduction_error(
    tmp_path: Path,
) -> None:
    write(
        tmp_path,
        "ex/parameters/claim_reduction/2025.yaml",
        CLAIM_REDUCTION_2025.replace('ceiling: "2834"', 'ceiling: "-1"'),
    )

    with pytest.raises(InvalidParameterDataError) as raised:
        source(tmp_path).get("ex/claim_reduction", 2025, CLAIM_REDUCTION)

    assert isinstance(raised.value.__cause__, InvalidClaimReductionError)


def test_reads_a_year_amounts_dataset(tmp_path: Path) -> None:
    write(tmp_path, "ex/parameters/year_amounts/2025.yaml", YEAR_AMOUNTS_2025)

    result = source(tmp_path).get("ex/year_amounts", 2025, YEAR_AMOUNTS)

    assert result == ParameterDataset(
        family="ex/year_amounts",
        tax_year=2025,
        kind=YEAR_AMOUNTS,
        values=YearAmounts(
            (
                YearAmountsRow(2024, {"interest_limit": D("350"), "other_limit": D("10.50")}),
                YearAmountsRow(2001, {"interest_limit": D("300"), "other_limit": D("9")}),
                YearAmountsRow(None, {"interest_limit": D("250"), "other_limit": D("8")}),
            )
        ),
        rounding=NO_ROUNDING,
        sources=("https://example.org/year-amounts-2025",),
    )


def test_reads_a_year_amounts_datasets_figures_exactly(tmp_path: Path) -> None:
    content = YEAR_AMOUNTS_2025.replace('other_limit: "10.50"', 'other_limit: "10.500"')
    write(tmp_path, "ex/parameters/year_amounts/2025.yaml", content)

    values = source(tmp_path).get("ex/year_amounts", 2025, YEAR_AMOUNTS).values

    assert str(values.rows[0].amount("other_limit")) == "10.500"
    assert values.rows[0].from_year == 2024
    assert values.rows[2].from_year is None


def test_reads_a_year_amounts_dataset_written_as_block_mappings(tmp_path: Path) -> None:
    content = YEAR_AMOUNTS_2025.split("rows:\n")[0] + (
        "rows:\n"
        "  - from_year: 2024\n"
        "    amounts:\n"
        '      interest_limit: "350"\n'
        "  - amounts:\n"
        '      interest_limit: "300"\n'
    )
    write(tmp_path, "ex/parameters/year_amounts/2025.yaml", content)

    values = source(tmp_path).get("ex/year_amounts", 2025, YEAR_AMOUNTS).values

    assert values.row_for(2024) == YearAmountsRow(2024, {"interest_limit": D("350")})
    assert values.row_for(1990) == YearAmountsRow(None, {"interest_limit": D("300")})


def test_reads_a_year_amounts_dataset_whose_rows_are_all_dated(tmp_path: Path) -> None:
    content = YEAR_AMOUNTS_2025.replace("  - amounts:", "  - from_year: 1990\n    amounts:")
    write(tmp_path, "ex/parameters/year_amounts/2025.yaml", content)

    values = source(tmp_path).get("ex/year_amounts", 2025, YEAR_AMOUNTS).values

    assert values.rows[2].from_year == 1990
    assert values.row_for(1989) is None


def test_reads_a_year_amounts_datasets_rounding_rule(tmp_path: Path) -> None:
    write(
        tmp_path,
        "ex/parameters/year_amounts/2025.yaml",
        YEAR_AMOUNTS_2025.replace("rounding: none", 'rounding: {increment: "0.01", mode: half_up}'),
    )

    result = source(tmp_path).get("ex/year_amounts", 2025, YEAR_AMOUNTS)

    assert result.rounding == RoundTo(D("0.01"), RoundingMode.HALF_UP)


def test_by_default_the_year_amounts_parser_comes_from_the_shared_registry(tmp_path: Path) -> None:
    write(tmp_path, "ex/parameters/year_amounts/2025.yaml", YEAR_AMOUNTS_2025)

    result = YamlParameterSource(roots(tmp_path), built_in_parsers()).get(
        "ex/year_amounts", 2025, YEAR_AMOUNTS
    )

    assert result.values.row_for(2010) == YearAmountsRow(
        2001, {"interest_limit": D("300"), "other_limit": D("9")}
    )


def test_a_year_amounts_dataset_is_not_a_rate_dataset(tmp_path: Path) -> None:
    write(tmp_path, "ex/parameters/year_amounts/2025.yaml", YEAR_AMOUNTS_2025)

    with pytest.raises(InvalidParameterDataError, match="kind 'year_amounts' does not match"):
        source(tmp_path).get("ex/year_amounts", 2025, RATE)


@pytest.mark.parametrize(
    ("content", "message"),
    [
        pytest.param(
            YEAR_AMOUNTS_2025.replace("from_year: 2024", 'from_year: "2024"'),
            r"rows\[0\].from_year must be an integer, got str",
            id="from-year-quoted",
        ),
        pytest.param(
            YEAR_AMOUNTS_2025.replace("from_year: 2024", "from_year: 2024.5"),
            r"rows\[0\].from_year must be an integer, got float",
            id="from-year-float",
        ),
        pytest.param(
            YEAR_AMOUNTS_2025.replace("from_year: 2024", "from_year: yes"),
            r"rows\[0\].from_year must be an integer, got bool",
            id="from-year-boolean",
        ),
        pytest.param(
            YEAR_AMOUNTS_2025.replace('interest_limit: "350"', "interest_limit: 350"),
            r"rows\[0\].amounts.interest_limit must be a string, got int",
            id="amount-as-yaml-number",
        ),
        pytest.param(
            YEAR_AMOUNTS_2025.replace('interest_limit: "300"', 'interest_limit: "lots"'),
            r"rows\[1\].amounts.interest_limit is not a decimal: 'lots'",
            id="amount-not-decimal",
        ),
        pytest.param(
            YEAR_AMOUNTS_2025.replace('interest_limit: "300"', 'interest_limit: "Infinity"'),
            r"rows\[1\].amounts.interest_limit is not a decimal",
            id="amount-infinite",
        ),
        pytest.param(
            YEAR_AMOUNTS_2025.replace('interest_limit: "250"', 'interest_limit: "-1"'),
            r"rows\[2\].*must not be negative",
            id="amount-negative",
        ),
        pytest.param(
            YEAR_AMOUNTS_2025.replace(
                '    amounts: {interest_limit: "350", other_limit: "10.50"}\n', ""
            ),
            r"rows\[0\]: missing keys \['amounts'\]",
            id="amounts-missing",
        ),
        pytest.param(
            YEAR_AMOUNTS_2025.replace(
                'amounts: {interest_limit: "350", other_limit: "10.50"}', "amounts: {}"
            ),
            r"rows\[0\].*at least one amount",
            id="amounts-empty",
        ),
        pytest.param(
            YEAR_AMOUNTS_2025.replace(
                'amounts: {interest_limit: "350", other_limit: "10.50"}', 'amounts: "350"'
            ),
            r"rows\[0\].amounts must be a mapping",
            id="amounts-not-a-mapping",
        ),
        pytest.param(
            YEAR_AMOUNTS_2025.replace('other_limit: "9"', 'third_limit: "9"'),
            "same amount names",
            id="amount-names-differ",
        ),
        pytest.param(
            YEAR_AMOUNTS_2025.replace("from_year: 2001", "from_year: 2024"),
            r"strictly descending",
            id="years-equal",
        ),
        pytest.param(
            YEAR_AMOUNTS_2025.replace("from_year: 2001", "from_year: 2030"),
            r"strictly descending",
            id="years-ascending",
        ),
        pytest.param(
            YEAR_AMOUNTS_2025.replace("  - from_year: 2001\n", "  - \n"),
            r"only the last row",
            id="open-ended-row-in-the-middle",
        ),
        pytest.param(
            YEAR_AMOUNTS_2025 + '  - amounts: {interest_limit: "1", other_limit: "1"}\n',
            r"only the last row",
            id="two-open-ended-rows",
        ),
        pytest.param(
            YEAR_AMOUNTS_2025.replace(
                'other_limit: "10.50"}', 'other_limit: "10.50"}\n    note: "x"'
            ),
            r"rows\[0\]: unknown keys \['note'\]",
            id="unknown-row-key",
        ),
        pytest.param(
            YEAR_AMOUNTS_2025.replace("rows:", "years:"),
            r"unknown keys \['years'\]",
            id="years-are-not-rows",
        ),
        pytest.param(
            YEAR_AMOUNTS_2025.split("rows:\n")[0] + "rows: []\n",
            "at least one row",
            id="no-rows",
        ),
        pytest.param(
            YEAR_AMOUNTS_2025.split("rows:\n")[0] + 'rows:\n  - "2024"\n',
            r"rows\[0\] must be a mapping",
            id="row-not-a-mapping",
        ),
        pytest.param(
            YEAR_AMOUNTS_2025.split("rows:\n")[0],
            r"missing keys \['rows'\]",
            id="rows-missing",
        ),
        pytest.param(
            YEAR_AMOUNTS_2025 + 'amount: "1"\n',
            r"unknown keys \['amount'\]",
            id="unknown-key",
        ),
    ],
)
def test_rejects_an_invalid_year_amounts_dataset(
    tmp_path: Path, content: str, message: str
) -> None:
    write(tmp_path, "ex/parameters/year_amounts/2025.yaml", content)

    with pytest.raises(InvalidParameterDataError, match=message) as excinfo:
        source(tmp_path).get("ex/year_amounts", 2025, YEAR_AMOUNTS)

    assert "2025.yaml" in str(excinfo.value)


def test_an_invalid_year_amounts_figure_is_reported_as_a_year_amounts_error(
    tmp_path: Path,
) -> None:
    write(
        tmp_path,
        "ex/parameters/year_amounts/2025.yaml",
        YEAR_AMOUNTS_2025.replace('interest_limit: "250"', 'interest_limit: "-1"'),
    )

    with pytest.raises(InvalidParameterDataError) as raised:
        source(tmp_path).get("ex/year_amounts", 2025, YEAR_AMOUNTS)

    assert isinstance(raised.value.__cause__, InvalidYearAmountsError)


@pytest.mark.parametrize(
    ("content", "message"),
    [
        pytest.param(
            CONTRIBUTION_TIER_2025.replace('rate: "0.05"', 'rate: "1.5"'),
            "rate must be between 0 and 1",
            id="rate-above-one",
        ),
        pytest.param(
            CONTRIBUTION_TIER_2025.replace('rate: "0.05"', 'rate: "-0.05"'),
            "rate must be between 0 and 1",
            id="rate-negative",
        ),
        pytest.param(
            CONTRIBUTION_TIER_2025.replace('rate: "0.05"', "rate: 0.05"),
            "rate must be a string, got float",
            id="rate-as-yaml-number",
        ),
        pytest.param(
            CONTRIBUTION_TIER_2025.replace('lower: "3000"', "lower: 3000"),
            "lower must be a string, got int",
            id="lower-as-yaml-number",
        ),
        pytest.param(
            CONTRIBUTION_TIER_2025.replace('upper: "50000"', "upper: 50000.5"),
            "upper must be a string, got float",
            id="upper-as-yaml-float",
        ),
        pytest.param(
            CONTRIBUTION_TIER_2025.replace('maximum: "2350"', "maximum: 2350"),
            "maximum must be a string, got int",
            id="maximum-as-yaml-number",
        ),
        pytest.param(
            CONTRIBUTION_TIER_2025.replace('lower: "3000"', 'lower: "lots"'),
            "lower is not a decimal: 'lots'",
            id="lower-not-decimal",
        ),
        pytest.param(
            CONTRIBUTION_TIER_2025.replace('upper: "50000"', 'upper: "Infinity"'),
            "upper is not a decimal",
            id="upper-infinite",
        ),
        pytest.param(
            CONTRIBUTION_TIER_2025.replace('maximum: "2350"', 'maximum: "NaN"'),
            "maximum is not a decimal",
            id="maximum-nan",
        ),
        pytest.param(
            CONTRIBUTION_TIER_2025.replace('lower: "3000"', 'lower: "-1"'),
            "lower must not be negative",
            id="lower-negative",
        ),
        pytest.param(
            CONTRIBUTION_TIER_2025.replace('lower: "3000"', 'lower: "50000"'),
            "lower must be below upper",
            id="lower-at-upper",
        ),
        pytest.param(
            CONTRIBUTION_TIER_2025.replace('upper: "50000"', 'upper: "2999.99"'),
            "lower must be below upper",
            id="upper-below-lower",
        ),
        pytest.param(
            CONTRIBUTION_TIER_2025.replace('maximum: "2350"', 'maximum: "-0.01"'),
            "maximum must not be negative",
            id="maximum-negative",
        ),
        pytest.param(
            CONTRIBUTION_TIER_2025.replace('upper: "50000"\n', ""),
            r"missing keys \['upper'\]",
            id="upper-missing",
        ),
        pytest.param(
            CONTRIBUTION_TIER_2025.replace('rate: "0.05"\n', "").replace('maximum: "2350"\n', ""),
            r"missing keys \['maximum', 'rate'\]",
            id="rate-and-maximum-missing",
        ),
        pytest.param(
            CONTRIBUTION_TIER_2025 + 'amount: "1000"\n',
            r"unknown keys \['amount'\]",
            id="amount-is-not-a-tier-key",
        ),
        pytest.param(
            CONTRIBUTION_TIER_2025.replace("kind: contribution_tier", "kind: rate"),
            "kind 'rate' does not match the requested 'contribution_tier'",
            id="kind-mismatch",
        ),
        pytest.param(
            CONTRIBUTION_TIER_2025.replace("rounding: none\n", ""),
            r"missing keys \['rounding'\]",
            id="rounding-missing",
        ),
        pytest.param(
            CONTRIBUTION_TIER_2025.replace(
                "sources:\n  - https://example.org/contribution-tier-2025", "sources: []"
            ),
            "sources must list at least one",
            id="sources-empty",
        ),
    ],
)
def test_rejects_malformed_contribution_tier_dataset(
    tmp_path: Path, content: str, message: str
) -> None:
    write(tmp_path, "ex/parameters/contribution_tier/2025.yaml", content)

    with pytest.raises(InvalidParameterDataError, match=message) as excinfo:
        source(tmp_path).get("ex/contribution_tier", 2025, CONTRIBUTION_TIER)

    assert "2025.yaml" in str(excinfo.value)


def test_an_invalid_tier_rate_is_reported_as_a_rate_error(tmp_path: Path) -> None:
    write(
        tmp_path,
        "ex/parameters/contribution_tier/2025.yaml",
        CONTRIBUTION_TIER_2025.replace('rate: "0.05"', 'rate: "1.5"'),
    )

    with pytest.raises(InvalidParameterDataError) as excinfo:
        source(tmp_path).get("ex/contribution_tier", 2025, CONTRIBUTION_TIER)

    assert isinstance(excinfo.value.__cause__, InvalidRateError)


@pytest.mark.parametrize(
    ("old", "new"),
    [
        ('lower: "3000"', 'lower: "-1"'),
        ('lower: "3000"', 'lower: "60000"'),
        ('maximum: "2350"', 'maximum: "-1"'),
    ],
)
def test_an_invalid_tier_is_reported_as_a_contribution_tier_error(
    tmp_path: Path, old: str, new: str
) -> None:
    write(
        tmp_path,
        "ex/parameters/contribution_tier/2025.yaml",
        CONTRIBUTION_TIER_2025.replace(old, new),
    )

    with pytest.raises(InvalidParameterDataError) as excinfo:
        source(tmp_path).get("ex/contribution_tier", 2025, CONTRIBUTION_TIER)

    assert isinstance(excinfo.value.__cause__, InvalidContributionTierError)


def test_a_rate_dataset_is_not_a_contribution_tier_dataset(tmp_path: Path) -> None:
    # Both kinds read a `rate` key; the declared kind alone tells them apart.
    write(tmp_path, "ex/parameters/credit_rate/2025.yaml", RATE_2025)

    with pytest.raises(InvalidParameterDataError, match="kind 'rate' does not match"):
        source(tmp_path).get("ex/credit_rate", 2025, CONTRIBUTION_TIER)


def test_a_contribution_tier_dataset_is_not_a_rate_dataset(tmp_path: Path) -> None:
    write(tmp_path, "ex/parameters/contribution_tier/2025.yaml", CONTRIBUTION_TIER_2025)

    with pytest.raises(InvalidParameterDataError, match="kind 'contribution_tier' does not match"):
        source(tmp_path).get("ex/contribution_tier", 2025, RATE)


@pytest.mark.parametrize(
    ("content", "message"),
    [
        pytest.param(
            TAPER_2025.replace('base: "1000"', "base: 1000"),
            "base must be a string, got int",
            id="base-as-yaml-number",
        ),
        pytest.param(
            TAPER_2025.replace('supplement: "500"', "supplement: 500.5"),
            "supplement must be a string, got float",
            id="supplement-as-yaml-float",
        ),
        pytest.param(
            TAPER_2025.replace('threshold: "20000"', "threshold: 20000"),
            "threshold must be a string, got int",
            id="threshold-as-yaml-number",
        ),
        pytest.param(
            TAPER_2025.replace('range: "10000"', "range: 10000"),
            "range must be a string, got int",
            id="range-as-yaml-number",
        ),
        pytest.param(
            TAPER_2025.replace('base: "1000"', 'base: "lots"'),
            "base is not a decimal: 'lots'",
            id="base-not-decimal",
        ),
        pytest.param(
            TAPER_2025.replace('threshold: "20000"', 'threshold: "Infinity"'),
            "threshold is not a decimal",
            id="threshold-infinite",
        ),
        pytest.param(
            TAPER_2025.replace('range: "10000"', 'range: "NaN"'),
            "range is not a decimal",
            id="range-nan",
        ),
        pytest.param(
            TAPER_2025.replace('base: "1000"', 'base: "-1"'),
            "base must not be negative",
            id="base-negative",
        ),
        pytest.param(
            TAPER_2025.replace('supplement: "500"', 'supplement: "-0.01"'),
            "supplement must not be negative",
            id="supplement-negative",
        ),
        pytest.param(
            TAPER_2025.replace('threshold: "20000"', 'threshold: "-1"'),
            "threshold must not be negative",
            id="threshold-negative",
        ),
        pytest.param(
            TAPER_2025.replace('range: "10000"', 'range: "0"'),
            "range must be positive",
            id="range-zero",
        ),
        pytest.param(
            TAPER_2025.replace('range: "10000"', 'range: "-10000"'),
            "range must be positive",
            id="range-negative",
        ),
        pytest.param(
            TAPER_2025.replace('range: "10000"\n', ""),
            r"missing keys \['range'\]",
            id="range-missing",
        ),
        pytest.param(
            TAPER_2025.replace('base: "1000"\n', "").replace('supplement: "500"\n', ""),
            r"missing keys \['base', 'supplement'\]",
            id="base-and-supplement-missing",
        ),
        pytest.param(
            TAPER_2025 + 'maximum: "1500"\n',
            r"unknown keys \['maximum'\]",
            id="maximum-is-not-a-taper-key",
        ),
        pytest.param(
            TAPER_2025.replace('range: "10000"', 'upper: "30000"'),
            r"unknown keys \['upper'\]",
            id="upper-instead-of-range",
        ),
        pytest.param(
            TAPER_2025.replace("kind: taper", "kind: amount"),
            "kind 'amount' does not match the requested 'taper'",
            id="kind-mismatch",
        ),
        pytest.param(
            TAPER_2025.replace("rounding: none\n", ""),
            r"missing keys \['rounding'\]",
            id="rounding-missing",
        ),
        pytest.param(
            TAPER_2025.replace("sources:\n  - https://example.org/taper-2025", "sources: []"),
            "sources must list at least one",
            id="sources-empty",
        ),
    ],
)
def test_rejects_malformed_taper_dataset(tmp_path: Path, content: str, message: str) -> None:
    write(tmp_path, "ex/parameters/taper/2025.yaml", content)

    with pytest.raises(InvalidParameterDataError, match=message) as excinfo:
        source(tmp_path).get("ex/taper", 2025, TAPER)

    assert "2025.yaml" in str(excinfo.value)


@pytest.mark.parametrize(
    ("old", "new"),
    [
        ('base: "1000"', 'base: "-1"'),
        ('supplement: "500"', 'supplement: "-1"'),
        ('threshold: "20000"', 'threshold: "-1"'),
        ('range: "10000"', 'range: "0"'),
    ],
)
def test_an_invalid_taper_is_reported_as_a_taper_error(tmp_path: Path, old: str, new: str) -> None:
    write(tmp_path, "ex/parameters/taper/2025.yaml", TAPER_2025.replace(old, new))

    with pytest.raises(InvalidParameterDataError) as excinfo:
        source(tmp_path).get("ex/taper", 2025, TAPER)

    assert isinstance(excinfo.value.__cause__, InvalidTaperError)


def test_an_amount_dataset_is_not_a_taper_dataset(tmp_path: Path) -> None:
    write(tmp_path, "ex/parameters/amount_cap/2025.yaml", AMOUNT_2025)

    with pytest.raises(InvalidParameterDataError, match="kind 'amount' does not match"):
        source(tmp_path).get("ex/amount_cap", 2025, TAPER)


def test_a_taper_dataset_is_not_a_credit_dataset(tmp_path: Path) -> None:
    write(tmp_path, "ex/parameters/taper/2025.yaml", TAPER_2025)

    with pytest.raises(InvalidParameterDataError, match="kind 'taper' does not match"):
        source(tmp_path).get("ex/taper", 2025, CREDIT)


@pytest.mark.parametrize(
    ("content", "message"),
    [
        pytest.param(
            AMOUNT_BY_COUNT_2025.replace('"2": "200.50"', '"2": 200.50'),
            "must be a string, got float",
            id="amount-as-yaml-float",
        ),
        pytest.param(
            AMOUNT_BY_COUNT_2025.replace('"2": "200.50"', '"2": 200'),
            "must be a string, got int",
            id="amount-as-yaml-number",
        ),
        pytest.param(
            AMOUNT_BY_COUNT_2025.replace('"1": "100"', '1: "100"'),
            "must be a string, got int",
            id="count-as-yaml-number",
        ),
        pytest.param(
            AMOUNT_BY_COUNT_2025.replace('"1": "100"', '"one": "100"'),
            "is not a whole number",
            id="count-not-digits",
        ),
        pytest.param(
            AMOUNT_BY_COUNT_2025.replace('"1": "100"', '"01": "100"'),
            "is not a whole number",
            id="count-leading-zero",
        ),
        pytest.param(
            AMOUNT_BY_COUNT_2025.replace('"1": "100"', '"-1": "100"'),
            "is not a whole number",
            id="count-negative",
        ),
        pytest.param(
            AMOUNT_BY_COUNT_2025.replace('"1": "100"', '"+1": "100"'),
            "is not a whole number",
            id="count-signed",
        ),
        pytest.param(
            AMOUNT_BY_COUNT_2025.replace('"1": "100"', '"1.5": "100"'),
            "is not a whole number",
            id="count-fractional",
        ),
        pytest.param(
            AMOUNT_BY_COUNT_2025.replace('"1": "100"', '" 1": "100"'),
            "is not a whole number",
            id="count-padded",
        ),
        pytest.param(
            AMOUNT_BY_COUNT_2025.replace('"1": "100"', '"": "100"'),
            "keys must not be empty|is not a whole number",
            id="count-empty",
        ),
        pytest.param(
            AMOUNT_BY_COUNT_2025.replace('"2": "200.50"', '"2": "lots"'),
            "is not a decimal: 'lots'",
            id="amount-not-decimal",
        ),
        pytest.param(
            AMOUNT_BY_COUNT_2025.replace('"2": "200.50"', '"2": "Infinity"'),
            "is not a decimal",
            id="amount-infinite",
        ),
        pytest.param(
            AMOUNT_BY_COUNT_2025.replace('"2": "200.50"', '"2": "NaN"'),
            "is not a decimal",
            id="amount-nan",
        ),
        pytest.param(
            AMOUNT_BY_COUNT_2025.replace('"2": "200.50"', '"2": "-0.01"'),
            "amount must not be negative",
            id="amount-negative",
        ),
        pytest.param(
            AMOUNT_BY_COUNT_2025.replace('"2": "200.50"', '"2": "200.50"\n  "2": "300"'),
            "duplicate key '2'",
            id="count-duplicated",
        ),
        pytest.param(
            AMOUNT_BY_COUNT_2025.replace(
                '  "1": "100"\n  "2": "200.50"\n  "3": "300"\n  "4": "400"\n', "  {}\n"
            ),
            "must not be empty",
            id="amounts-empty",
        ),
        pytest.param(
            AMOUNT_BY_COUNT_2025.replace(
                '  "1": "100"\n  "2": "200.50"\n  "3": "300"\n  "4": "400"\n', '  - "100"\n'
            ),
            "amounts must be a mapping",
            id="amounts-as-a-list",
        ),
        pytest.param(
            AMOUNT_BY_COUNT_2025.replace(
                'amounts:\n  "1": "100"\n  "2": "200.50"\n  "3": "300"\n  "4": "400"\n',
                'amounts: "100"\n',
            ),
            "amounts must be a mapping",
            id="amounts-as-a-string",
        ),
        pytest.param(
            AMOUNT_BY_COUNT_2025.replace(
                'amounts:\n  "1": "100"\n  "2": "200.50"\n  "3": "300"\n  "4": "400"\n', ""
            ),
            r"missing keys \['amounts'\]",
            id="amounts-missing",
        ),
        pytest.param(
            AMOUNT_BY_COUNT_2025 + 'amount: "100"\n',
            r"unknown keys \['amount'\]",
            id="amount-is-not-an-amount-by-count-key",
        ),
        pytest.param(
            AMOUNT_BY_COUNT_2025.replace("kind: amount_by_count", "kind: amount"),
            "kind 'amount' does not match the requested 'amount_by_count'",
            id="kind-mismatch",
        ),
        pytest.param(
            AMOUNT_BY_COUNT_2025.replace("rounding: none\n", ""),
            r"missing keys \['rounding'\]",
            id="rounding-missing",
        ),
        pytest.param(
            AMOUNT_BY_COUNT_2025.replace(
                "sources:\n  - https://example.org/amount-by-count-2025", "sources: []"
            ),
            "sources must list at least one",
            id="sources-empty",
        ),
    ],
)
def test_rejects_malformed_amount_by_count_dataset(
    tmp_path: Path, content: str, message: str
) -> None:
    write(tmp_path, "ex/parameters/amount_by_count/2025.yaml", content)

    with pytest.raises(InvalidParameterDataError, match=message) as excinfo:
        source(tmp_path).get("ex/amount_by_count", 2025, AMOUNT_BY_COUNT)

    assert "2025.yaml" in str(excinfo.value)


def test_a_negative_amount_is_reported_as_an_amount_by_count_error(tmp_path: Path) -> None:
    content = AMOUNT_BY_COUNT_2025.replace('"2": "200.50"', '"2": "-1"')
    write(tmp_path, "ex/parameters/amount_by_count/2025.yaml", content)

    with pytest.raises(InvalidParameterDataError) as excinfo:
        source(tmp_path).get("ex/amount_by_count", 2025, AMOUNT_BY_COUNT)

    assert isinstance(excinfo.value.__cause__, InvalidAmountByCountError)


def test_an_empty_amount_by_count_is_reported_as_an_amount_by_count_error(
    tmp_path: Path,
) -> None:
    content = AMOUNT_BY_COUNT_2025.replace(
        '  "1": "100"\n  "2": "200.50"\n  "3": "300"\n  "4": "400"\n', "  {}\n"
    )
    write(tmp_path, "ex/parameters/amount_by_count/2025.yaml", content)

    with pytest.raises(InvalidParameterDataError) as excinfo:
        source(tmp_path).get("ex/amount_by_count", 2025, AMOUNT_BY_COUNT)

    assert isinstance(excinfo.value.__cause__, InvalidAmountByCountError)


def test_an_amount_dataset_is_not_an_amount_by_count_dataset(tmp_path: Path) -> None:
    write(tmp_path, "ex/parameters/amount_cap/2025.yaml", AMOUNT_2025)

    with pytest.raises(InvalidParameterDataError, match="kind 'amount' does not match"):
        source(tmp_path).get("ex/amount_cap", 2025, AMOUNT_BY_COUNT)


def test_an_amount_by_count_dataset_is_not_an_amount_dataset(tmp_path: Path) -> None:
    write(tmp_path, "ex/parameters/amount_by_count/2025.yaml", AMOUNT_BY_COUNT_2025)

    with pytest.raises(InvalidParameterDataError, match="kind 'amount_by_count' does not match"):
        source(tmp_path).get("ex/amount_by_count", 2025, AMOUNT)
