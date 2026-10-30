"""The 2025 principal residence rounding rule (Form T2091(IND) Part 1 line 23), checked against
CRA's form.

2025 Form T2091(IND), Designation of a Property as a Principal Residence by an Individual (Other
than a Personal Trust), Section 2, Part 1: "Line 4 plus 1 (see note on page 4)" (line 20),
"Multiply line 19 by line 20." (line 21), "Total number of years from line 7" (line 22) and
"Divide line 21 by line 22." (line 23). Line 23 divides, so its one dataset is a `rounding_only`
one: the quotient is a dollars-and-cents box, rounded half-up to the cent, the owner's decision, as
the form states no rounding rule. The other lines only add, subtract and multiply amounts in cents
by whole numbers of years, so they have no dataset. The form is a PDF with no published .txt, so
the dataset cites the PDF.

The dataset is tested with the capability that reads it, on the registered kinds; the lines
together, from the two properties to Schedule 3 line 15800, are in the `end_to_end` tests and
`returns/2025_return_ai.yaml`.
"""

from __future__ import annotations

import re
from decimal import Decimal
from typing import Any

import pytest

import tax_engine.registrations
from tax_engine.adapters.outbound.yaml_parameters import YamlParameterSource
from tax_engine.domain.artifact import Artifact, ArtifactKind
from tax_engine.domain.parameters.rounding import RoundingMode, RoundTo
from tax_engine.domain.parameters.rounding_only import ROUNDING_ONLY, RoundingOnly
from tax_engine.domain.record_list import RecordList
from tax_engine.domain.registry import Namespace
from tax_engine.jurisdictions.ca.capabilities.principal_residence_gain import (
    PrincipalResidenceGain,
)
from tax_engine.jurisdictions.ca.catalog import (
    PRINCIPAL_RESIDENCE_GAIN,
    PRINCIPAL_RESIDENCE_PROPERTIES,
    RESIDENCE_ADJUSTED_COST_BASE,
    RESIDENCE_ADJUSTED_COST_BASE_DEC_31_1981,
    RESIDENCE_COST_BASE_ADJUSTMENTS_AFTER_1981,
    RESIDENCE_FMV_DEC_31_1981,
    RESIDENCE_OUTLAYS,
    RESIDENCE_PART_2_APPLIES,
    RESIDENCE_PLUS_ONE_YEAR,
    RESIDENCE_PROCEEDS,
    RESIDENCE_T664_FILED,
    RESIDENCE_WS_ADJUSTED_COST_BASE_FEB_22_1994,
    RESIDENCE_WS_COST_BASE_ADJUSTMENTS_TO_FEB_1994,
    RESIDENCE_WS_DESIGNATED_PROCEEDS,
    RESIDENCE_WS_ELECTED_CAPITAL_GAIN,
    RESIDENCE_WS_FMV_FEB_22_1994,
    RESIDENCE_WS_MONTHS_OWNED_AFTER_1971,
    RESIDENCE_WS_MONTHS_OWNED_AFTER_FEB_1992,
    RESIDENCE_WS_YEARS_DESIGNATED_AFTER_1981,
    RESIDENCE_WS_YEARS_OWNED_AFTER_1981,
    RESIDENCE_YEARS_DESIGNATED_1972_TO_1981,
    RESIDENCE_YEARS_DESIGNATED_AFTER_1981,
    RESIDENCE_YEARS_OWNED_1972_TO_1981,
    RESIDENCE_YEARS_OWNED_AFTER_1981,
)

D = Decimal
SOURCE = YamlParameterSource(tax_engine.registrations.JURISDICTIONS.roots())
CENT = RoundTo(D("0.01"), RoundingMode.HALF_UP)
FAMILY = "ca/principal_residence_gain_rounding"
T2091_PDF = "https://www.canada.ca/content/dam/cra-arc/formspubs/pbg/t2091ind/t2091ind-25e.pdf"


def squashed(text: str) -> str:
    """`text` with the comment markers and line breaks gone and runs of blanks made one."""
    return re.sub(r"\s+", " ", text.replace("#", " ")).strip()


def dataset_header(family: str) -> str:
    """The comment lines above the dataset's first key, squashed."""
    root = tax_engine.registrations.JURISDICTIONS.roots()[Namespace("ca")]
    name = family.removeprefix("ca/")
    lines = (root / "parameters" / name / "2025.yaml").read_text().splitlines()
    first_key = next(i for i, line in enumerate(lines) if line[:1] != "#")
    return squashed("\n".join(lines[:first_key]))


def test_2025_rounding_is_half_up_to_the_cent_with_no_other_figure() -> None:
    data = SOURCE.get(FAMILY, 2025, ROUNDING_ONLY)

    assert data.values == RoundingOnly()
    # Line 23, a dollars-and-cents box: half-up to the cent.
    assert data.rounding == CENT


def test_2025_dataset_cites_only_the_t2091_ind_pdf() -> None:
    assert SOURCE.get(FAMILY, 2025, ROUNDING_ONLY).sources == (T2091_PDF,)


def test_the_dataset_header_quotes_t2091_ind_as_the_form_prints_it() -> None:
    header = dataset_header(FAMILY)

    for quoted in (
        "Multiply line 19 by line 20.",
        "Total number of years from line 7",
        "Divide line 21 by line 22.",
    ):
        assert quoted in header, quoted


def test_the_dataset_header_states_the_half_up_cent_rule() -> None:
    header = dataset_header(FAMILY).lower()

    assert "dollars-and-cents box" in header
    assert "half-up" in header


def properties(*rows: tuple[int, int, str, str, str, int]) -> Artifact[RecordList]:
    """A `ca/principal_residence_properties` artifact of one record per (years designated after
    1981, years owned after 1981, proceeds, outlays, adjusted cost base, plus one) row."""
    records: list[dict[ArtifactKind[Any], object]] = [
        {
            RESIDENCE_YEARS_DESIGNATED_AFTER_1981: designated,
            RESIDENCE_YEARS_DESIGNATED_1972_TO_1981: 0,
            RESIDENCE_YEARS_OWNED_AFTER_1981: owned,
            RESIDENCE_YEARS_OWNED_1972_TO_1981: 0,
            RESIDENCE_PROCEEDS: D(proceeds),
            RESIDENCE_OUTLAYS: D(outlays),
            RESIDENCE_ADJUSTED_COST_BASE: D(cost_base),
            RESIDENCE_PLUS_ONE_YEAR: plus_one,
            RESIDENCE_PART_2_APPLIES: 0,
            RESIDENCE_ADJUSTED_COST_BASE_DEC_31_1981: D("0"),
            RESIDENCE_FMV_DEC_31_1981: D("0"),
            RESIDENCE_COST_BASE_ADJUSTMENTS_AFTER_1981: D("0"),
            RESIDENCE_T664_FILED: 0,
            RESIDENCE_WS_YEARS_DESIGNATED_AFTER_1981: 0,
            RESIDENCE_WS_YEARS_OWNED_AFTER_1981: 0,
            RESIDENCE_WS_DESIGNATED_PROCEEDS: D("0"),
            RESIDENCE_WS_ADJUSTED_COST_BASE_FEB_22_1994: D("0"),
            RESIDENCE_WS_FMV_FEB_22_1994: D("0"),
            RESIDENCE_WS_ELECTED_CAPITAL_GAIN: D("0"),
            RESIDENCE_WS_MONTHS_OWNED_AFTER_FEB_1992: 0,
            RESIDENCE_WS_MONTHS_OWNED_AFTER_1971: 0,
            RESIDENCE_WS_COST_BASE_ADJUSTMENTS_TO_FEB_1994: Decimal("0"),
        }
        for designated, owned, proceeds, outlays, cost_base, plus_one in rows
    ]
    return Artifact(
        PRINCIPAL_RESIDENCE_PROPERTIES, RecordList(PRINCIPAL_RESIDENCE_PROPERTIES.fields, records)
    )


def line_54(*rows: tuple[int, int, str, str, str, int]) -> Decimal:
    capability = PrincipalResidenceGain(
        SOURCE.get(FAMILY, 2025, ROUNDING_ONLY),
        PRINCIPAL_RESIDENCE_PROPERTIES,
        PRINCIPAL_RESIDENCE_GAIN,
    )
    (output,) = capability.compute((properties(*rows),)).outputs
    assert output.kind == PRINCIPAL_RESIDENCE_GAIN
    assert isinstance(output.value, Decimal)
    return output.value


@pytest.mark.parametrize(
    ("rows", "expected"),
    [
        # The worked example: a gain of 300000.00, 6 of 10 years designated, plus one.
        (((6, 10, "400000.00", "5000.00", "95000.00", 1),), "90000.00"),
        ((), "0"),
        # Gain 70000.00 x 2 / 6 = 23333.333..., down to 23333.33; 70000.00 - 23333.33.
        (((1, 6, "250000.00", "0.00", "180000.00", 1),), "46666.67"),
        # Gain 0.01 x 1 / 2 = 0.005, a tie, up to 0.01; so 0.01 - 0.01 = 0.00.
        (((0, 2, "0.01", "0", "0", 1),), "0.00"),
        # Gain 0.03 x 1 / 2 = 0.015, a tie, up to 0.02; so 0.03 - 0.02 = 0.01.
        (((0, 2, "0.03", "0", "0", 1),), "0.01"),
        # Gain 0.01 x 1 / 3 = 0.00333..., down to 0.00; so 0.01 - 0.00 = 0.01.
        (((0, 3, "0.01", "0", "0", 1),), "0.01"),
        # Each property is rounded on its own before the gains are added: 46666.67 + 0.01.
        (
            (
                (1, 6, "250000.00", "0.00", "180000.00", 1),
                (0, 3, "0.01", "0", "0", 1),
            ),
            "46666.68",
        ),
    ],
)
def test_line_23_is_rounded_half_up_to_the_cent_before_it_is_taken_off_the_gain(
    rows: tuple[tuple[int, int, str, str, str, int], ...], expected: str
) -> None:
    assert line_54(*rows) == D(expected)
