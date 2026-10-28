"""The 2025 non-compliant CCA for short-term rentals (T776 Chart B, line 9367), checked against
CRA's form.

2025 Form T776 (Statement of Real Estate Rentals), Chart B: "Column 4: Related portion of the
available CCA from column 21 in Area A", "Column 7 ***: Non-compliant amount (column 4 multiplied
by column 5 divided by column 6)", "*** For each class, add the amounts from column 7 of Chart B
and enter each total in column 22 of Area A, in the respective row." and "Line C: Total
non-compliant amount of CCA for short-term rentals: Total of column 7 (enter on line 9367 of Part
4)". Line 9367 has no figure of its own, so its one dataset is a `rounding_only` one: each row of
column 7 is a dollars-and-cents box, rounded half-up to the cent, the owner's decision, as the
form states no rounding rule. The dataset is tested with the two capabilities that read it, on the
registered kinds; the lines together are in `end_to_end/test_return_av.py` and
`returns/2025_return_av.yaml`.
"""

from __future__ import annotations

import re
from decimal import Decimal
from pathlib import Path

import pytest

import tax_calculator.registrations
from tax_calculator.adapters.outbound.yaml_parameters import YamlParameterSource
from tax_calculator.domain.parameters.rounding import RoundingMode, RoundTo
from tax_calculator.domain.parameters.rounding_only import ROUNDING_ONLY, RoundingOnly
from tax_calculator.domain.record_list import RecordList
from tax_calculator.domain.registry import Namespace
from tax_calculator.jurisdictions.ca.capabilities import (
    short_term_rental_non_compliant_cca_by_class as rental_cca,
)
from tax_calculator.jurisdictions.ca.capabilities.short_term_rental_non_compliant_cca import (
    ShortTermRentalNonCompliantCca,
)
from tax_calculator.jurisdictions.ca.catalog import (
    CCA_CLASS_NUMBER,
    NON_COMPLIANT_CCA,
    RENTAL_NON_COMPLIANT_CCA,
    SHORT_TERM_RENTAL_CCA_UNITS,
    SHORT_TERM_RENTAL_NON_COMPLIANT_CCA_BY_CLASS,
)
from tests.jurisdictions.ca.capabilities.short_term_rental_cca import Row, units

D = Decimal
SOURCE = YamlParameterSource(tax_calculator.registrations.JURISDICTIONS.roots())
CENT = RoundTo(D("0.01"), RoundingMode.HALF_UP)
FAMILY = "ca/short_term_rental_non_compliant_cca_rounding"
T776_TEXT = "https://www.canada.ca/content/dam/cra-arc/formspubs/pbg/t776/t776-25e.txt"
T776_FILE = Path(__file__).parents[3] / "tests" / "fixtures" / "cra-forms-2025" / "t776-25e.txt"


def squashed(text: str) -> str:
    """`text` with the comment markers and line breaks gone and runs of blanks made one."""
    return re.sub(r"\s+", " ", text.replace("#", " ")).strip()


def dataset_header(family: str) -> str:
    """The comment lines above the dataset's first key, squashed."""
    root = tax_calculator.registrations.JURISDICTIONS.roots()[Namespace("ca")]
    name = family.removeprefix("ca/")
    lines = (root / "parameters" / name / "2025.yaml").read_text().splitlines()
    first_key = next(i for i, line in enumerate(lines) if line[:1] != "#")
    return squashed("\n".join(lines[:first_key]))


def test_2025_rounding_is_half_up_to_the_cent_with_no_other_figure() -> None:
    data = SOURCE.get(FAMILY, 2025, ROUNDING_ONLY)

    assert data.values == RoundingOnly()
    # Chart B column 7, a dollars-and-cents box: half-up to the cent.
    assert data.rounding == CENT


def test_2025_dataset_cites_only_the_t776_text() -> None:
    assert SOURCE.get(FAMILY, 2025, ROUNDING_ONLY).sources == (T776_TEXT,)


def test_the_dataset_header_quotes_t776_as_the_form_prints_it() -> None:
    header = dataset_header(FAMILY).lower()
    form = squashed(T776_FILE.read_text(encoding="utf-8-sig")).lower()

    for quoted in (
        "column 7 ***: non-compliant amount (column 4 multiplied by column 5 divided by column 6)",
        "line c: total non-compliant amount of cca for short-term rentals: total of column 7 "
        "(enter on line 9367 of part 4)",
    ):
        assert quoted in header, quoted
        assert quoted in form, quoted


def test_the_dataset_header_states_the_half_up_cent_rule() -> None:
    header = dataset_header(FAMILY).lower()

    assert "dollars-and-cents box" in header
    assert "half-up" in header


def test_the_form_text_in_the_repository_is_the_text_the_wiring_is_checked_against() -> None:
    t776 = squashed(T776_FILE.read_text(encoding="utf-8-sig"))

    for printed in (
        "Column 1: Class number ^",
        "Column 4: Related portion of the available CCA from column 21 in Area A ^",
        "Column 6: Number of days the residential property was a short-term rental ^",
        "Column 7 ***: Non-compliant amount (column 4 multiplied by column 5 divided by column 6)",
        "*** For each class, add the amounts from column 7 of Chart B and enter each total in"
        " column 22 of Area A, in the respective row.",
        "Line C: Total non-compliant amount of CCA for short-term rentals: Total of column 7"
        " (enter on line 9367 of Part 4)",
        "Column 22: Non-compliant amount of CCA (see Chart B below)",
    ):
        assert printed in t776, printed


def line_9367(*rows: Row) -> Decimal:
    capability = ShortTermRentalNonCompliantCca(
        SOURCE.get(FAMILY, 2025, ROUNDING_ONLY),
        SHORT_TERM_RENTAL_CCA_UNITS,
        RENTAL_NON_COMPLIANT_CCA,
    )
    (output,) = capability.compute((units(*rows),)).outputs
    assert output.kind == RENTAL_NON_COMPLIANT_CCA
    assert isinstance(output.value, Decimal)
    return output.value


@pytest.mark.parametrize(
    ("rows", "expected"),
    [
        # The ticket's example: 900 of related CCA, 30 non-compliant days of 90.
        ((("1", "900", 30, 90),), "300.00"),
        ((), "0"),
        # 100 x 2 / 3 = 66.666..., half-up to 66.67.
        ((("1", "100", 2, 3),), "66.67"),
        # 0.03 x 1 / 2 = 0.015, a tie, up to 0.02; 0.01 x 1 / 3 = 0.00333..., down to 0.00.
        ((("1", "0.03", 1, 2),), "0.02"),
        ((("1", "0.01", 1, 3),), "0.00"),
        # Each row is rounded on its own before the rows are added: 66.67 + 300.00.
        ((("1", "900", 30, 90), ("8", "100", 2, 3)), "366.67"),
    ],
)
def test_line_9367_is_chart_b_line_c_with_each_row_rounded_half_up_to_the_cent(
    rows: tuple[Row, ...], expected: str
) -> None:
    assert line_9367(*rows) == D(expected)


def test_column_22_is_the_total_of_column_7_for_each_class_rounded_half_up_to_the_cent() -> None:
    capability = rental_cca.ShortTermRentalNonCompliantCcaByClass(
        SOURCE.get(FAMILY, 2025, ROUNDING_ONLY),
        SHORT_TERM_RENTAL_CCA_UNITS,
        SHORT_TERM_RENTAL_NON_COMPLIANT_CCA_BY_CLASS,
    )

    (output,) = capability.compute(
        (units(("1", "900", 30, 90), ("1", "100", 1, 3), ("8", "500", 45, 90)),)
    ).outputs

    assert isinstance(output.value, RecordList)
    assert [(r[CCA_CLASS_NUMBER], r[NON_COMPLIANT_CCA]) for r in output.value.records] == [
        (D("1"), D("333.33")),
        (D("8"), D("250.00")),
    ]
