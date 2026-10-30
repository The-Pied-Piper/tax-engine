"""The 2025 datasets of the dispositions that Form T657 (2025) charts take "from line 6 / line 12 of
Form T2017", checked against the printed form.

Each Form T657 chart takes the amount from line 6 of Form T2017 (QFFP) and line 12 (QSBCS) for the
dispositions it names: Chart 2016 to Chart 2023 "do not include reserves from dispositions ... in
any year other than" its year, Chart 2024 Period 1 and Period 2 "in any year or period other than"
its period, Chart 2025 Part 1 "only include reserves reported on a T5013 slip or letter from
dispositions ... for Period 1 of 2024" and Chart 2025 Part 2 "do not include any reserves claimed on
dispositions ... before 2025 or in Period 1 of 2024 that is reported on a 2025 T5013 slip or in a
letter to the partner". Each dataset is a condition, or conditions, of the counts of a Form T2017
reserve record:
1 the years after the disposition (2025 less the year), 2 disposed of in Period 1 of 2024, 3
reserve reported on a T5013 slip or letter and 4 partnership year began before June 25, 2024 (Guide
T4037 sends a Period 1 reserve a partnership reports to Chart 2025 Part 1 or Chart 2024 Period 1 by
it). The count is a whole number, so nothing is rounded.
"""

from __future__ import annotations

from decimal import Decimal
from pathlib import Path

import pytest

import tax_engine.registrations
from tax_engine.adapters.outbound.yaml_parameters import YamlParameterSource
from tax_engine.domain.parameters.conditions import (
    CONDITIONS,
    Condition,
    ConditionList,
    ConditionPart,
    ConditionTest,
)
from tax_engine.domain.parameters.rounding import NO_ROUNDING

D = Decimal
SOURCE = YamlParameterSource(tax_engine.registrations.JURISDICTIONS.roots())
T657_PDF = "https://www.canada.ca/content/dam/cra-arc/formspubs/pbg/t657/t657-25e.pdf"

# The datasets and the counts each condition requires, as (position, figure) in order, one tuple for
# each condition (a disposition is taken when any one of them applies).
DATASETS = {
    **{
        f"ca/t657_chart_{year}_dispositions": (((1, str(2025 - year)),),)
        for year in range(2016, 2024)
    },
    # Guide T4037: a Period 1 reserve not reported on a slip, or reported by a partnership whose
    # fiscal period began after June 25, 2024, is Chart 2024 Period 1; the rest is Chart 2025
    # Part 1.
    "ca/t657_chart_2024_period_1_dispositions": (
        ((1, "1"), (2, "1"), (3, "0")),
        ((1, "1"), (2, "1"), (4, "0")),
    ),
    "ca/t657_chart_2024_period_2_dispositions": (((1, "1"), (2, "0")),),
    "ca/t657_chart_2025_part_1_dispositions": (((1, "1"), (2, "1"), (3, "1"), (4, "1")),),
    "ca/t657_chart_2025_part_2_dispositions": (((1, "0"),),),
}


@pytest.mark.parametrize(("family", "required"), DATASETS.items())
def test_2025_the_dataset_is_conditions_of_equal_counts_that_give_1_when_one_applies(
    family: str, required: tuple[tuple[tuple[int, str], ...], ...]
) -> None:
    data = SOURCE.get(family, 2025, CONDITIONS)

    assert data.values.count_when_any_applies == 1
    assert len(data.values.conditions) == len(required)
    for condition, counts in zip(data.values.conditions, required, strict=True):
        assert condition.parts == tuple(
            ConditionPart((ConditionTest("count", position, "equal_to", D(figure), None),))
            for position, figure in counts
        )
        assert isinstance(condition, Condition)
    assert data.values.count_positions_read == frozenset(
        position for counts in required for position, _ in counts
    )
    assert data.values.amount_positions_read == frozenset()
    assert isinstance(data.values, ConditionList)


@pytest.mark.parametrize("family", DATASETS)
def test_2025_the_dataset_cites_the_form_it_is_printed_on_and_rounds_nothing(
    family: str,
) -> None:
    data = SOURCE.get(family, 2025, CONDITIONS)

    assert T657_PDF in data.sources
    assert data.rounding == NO_ROUNDING


def test_each_period_total_pairs_every_row_list_with_the_export_of_its_own_row_form() -> None:
    # `rows[i]` and `amounts[i]` must come from the same line: the capability can only check the
    # lengths, so this pins the pairing of all 24 steps and the lines QFFP (2 to 4) and QSBCS (8 to
    # 10) each product reads.
    import yaml

    import tax_engine.jurisdictions.ca_on

    manifests = Path(tax_engine.jurisdictions.ca_on.__file__).parent / "manifests" / "v1"
    part = yaml.safe_load((manifests / "04d_t657_chart_amounts_from_t2017.yaml").read_text())
    steps = part["capabilities"]
    assert len(steps) == 24
    for step in steps:
        rows = step["consumes"]["rows"]
        amounts = step["consumes"]["amounts"]
        lines = [r.removeprefix("ca/t2017_line_").removesuffix("_reserve_rows") for r in rows]
        assert amounts == [f"ca/t2017_line_{n}_reserve.t2017_row_change" for n in lines]
        assert lines in (["2", "3", "4"], ["8", "9", "10"])
        product = step["produces"]["total"]
        qffp = product.rsplit("_", 1)[1] in {"d", "f", "i"}
        assert lines == (["2", "3", "4"] if qffp else ["8", "9", "10"]), product
