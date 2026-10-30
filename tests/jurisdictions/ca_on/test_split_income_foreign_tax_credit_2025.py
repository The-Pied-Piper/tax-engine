"""The 2025 foreign tax credit on split income rounding datasets (Form T1206 lines 23 and 49).

Form T1206 2025 (docs/cra-forms-2025/t1206-25e.pdf, confirmed 2026-10-19 from the PDF; no .txt
published), Part 2, "Federal foreign tax credit on split income": "Part of the amount on line 3 that
is from foreign sources" (68370) over "Total income from foreign sources" (68380), "× Amount from
line 40500 of your return" (line 23); "Line 22 minus line 23 (if negative, enter "0")" (line 24).

Part 3, "Provincial or territorial foreign tax credit on split income": "Part of the amount from
line 68370 on page 8 that is non-business income" over "Part of the amount from line 68380 on page
8 that is non-business income", "× Amount from line number of your Form 428 shown in column 7 in
Chart C on page 5" (line 49); "Line 48 minus line 49" (line 50).

Lines 23 and 49 multiply and divide, so each has one `rounding_only` dataset,
`ca/split_income_line_23_rounding` and `ca-on/split_income_line_49_rounding`: each is a
dollars-and-cents box, so the product over the quotient rounds half-up to the cent once, the
owner's decision, as the form states no rounding rule. Lines 24 and 50 take amounts already in
cents.

The dataset is tested with the capability that reads it, on made-up kinds.
"""

from __future__ import annotations

import re
from decimal import Decimal

import tax_engine.registrations
from tax_engine.adapters.outbound.yaml_parameters import YamlParameterSource
from tax_engine.domain.artifact import Artifact, ArtifactKind
from tax_engine.domain.parameters.rounding import RoundingMode, RoundTo
from tax_engine.domain.parameters.rounding_only import ROUNDING_ONLY, RoundingOnly
from tax_engine.domain.registry import Namespace
from tax_engine.jurisdictions.ca.capabilities.apply_ratio_or_zero import ApplyRatioOrZero

D = Decimal
SOURCE = YamlParameterSource(tax_engine.registrations.JURISDICTIONS.roots())
CENT = RoundTo(D("0.01"), RoundingMode.HALF_UP)
LINE_23_ROUNDING = "ca/split_income_line_23_rounding"
LINE_49_ROUNDING = "ca-on/split_income_line_49_rounding"
T1206_PDF = "https://www.canada.ca/content/dam/cra-arc/formspubs/pbg/t1206/t1206-25e.pdf"

# Made up for this test and not registered.
CREDIT = ArtifactKind("ex/credit", Decimal, non_negative=True)
FOREIGN_PART = ArtifactKind("ex/foreign_part", Decimal, non_negative=True)
FOREIGN_TOTAL = ArtifactKind("ex/foreign_total", Decimal, non_negative=True)
SHARE_OF_CREDIT = ArtifactKind("ex/share_of_credit", Decimal, non_negative=True)


def squashed(text: str) -> str:
    """`text` with the comment markers and line breaks gone and runs of blanks made one."""
    return re.sub(r"\s+", " ", text.replace("#", " ")).strip()


def dataset_header(family: str, namespace: str) -> str:
    """The comment lines above the dataset's first key, squashed."""
    root = tax_engine.registrations.JURISDICTIONS.roots()[Namespace(namespace)]
    name = family.removeprefix(f"{namespace}/")
    lines = (root / "parameters" / name / "2025.yaml").read_text().splitlines()
    first_key = next(i for i, line in enumerate(lines) if line[:1] != "#")
    return squashed("\n".join(lines[:first_key]))


def shared(family: str, credit: str, foreign_part: str, foreign_total: str) -> Decimal:
    capability = ApplyRatioOrZero(
        SOURCE.get(family, 2025, ROUNDING_ONLY),
        CREDIT,
        FOREIGN_PART,
        FOREIGN_TOTAL,
        SHARE_OF_CREDIT,
    )
    (output,) = capability.compute(
        (
            Artifact(CREDIT, D(credit)),
            Artifact(FOREIGN_PART, D(foreign_part)),
            Artifact(FOREIGN_TOTAL, D(foreign_total)),
        )
    ).outputs
    assert isinstance(output.value, Decimal)
    return output.value


def line_23(credit: str, foreign_part: str, foreign_total: str) -> Decimal:
    return shared(LINE_23_ROUNDING, credit, foreign_part, foreign_total)


def line_49(credit: str, foreign_part: str, foreign_total: str) -> Decimal:
    return shared(LINE_49_ROUNDING, credit, foreign_part, foreign_total)


def test_2025_line_23_rounding_is_half_up_to_the_cent_with_no_other_figure() -> None:
    data = SOURCE.get(LINE_23_ROUNDING, 2025, ROUNDING_ONLY)

    assert data.values == RoundingOnly()
    assert data.rounding == CENT


def test_2025_line_23_rounding_cites_only_the_t1206_pdf() -> None:
    assert SOURCE.get(LINE_23_ROUNDING, 2025, ROUNDING_ONLY).sources == (T1206_PDF,)


def test_the_line_23_header_quotes_t1206_as_the_form_prints_it() -> None:
    header = dataset_header(LINE_23_ROUNDING, "ca")

    for quoted in (
        "Part of the amount on line 3 that is from foreign sources",
        "Total income from foreign sources",
        "× Amount from line 40500 of your return",
    ):
        assert quoted in header, quoted


def test_the_line_23_header_states_the_half_up_cent_rule() -> None:
    header = dataset_header(LINE_23_ROUNDING, "ca").lower()

    assert "dollars-and-cents box" in header
    assert "half-up" in header
    assert "owner decided" in header or "owner's decision" in header


def test_line_23_is_the_credit_times_the_foreign_share_rounded_once() -> None:
    # 500.00 × 1000 / 3000 = 166.666..., rounded half-up to the cent once, not after the quotient.
    assert line_23("500.00", "1000", "3000") == D("166.67")
    assert line_23("500.00", "1500", "3000") == D("250.00")


def test_line_23_is_zero_when_there_is_no_income_from_foreign_sources() -> None:
    assert line_23("500.00", "0", "0") == D("0.00")


def test_2025_line_49_rounding_is_half_up_to_the_cent_with_no_other_figure() -> None:
    data = SOURCE.get(LINE_49_ROUNDING, 2025, ROUNDING_ONLY)

    assert data.values == RoundingOnly()
    assert data.rounding == CENT


def test_2025_line_49_rounding_cites_only_the_t1206_pdf() -> None:
    assert SOURCE.get(LINE_49_ROUNDING, 2025, ROUNDING_ONLY).sources == (T1206_PDF,)


def test_the_line_49_header_quotes_t1206_as_the_form_prints_it() -> None:
    header = dataset_header(LINE_49_ROUNDING, "ca-on")

    for quoted in (
        "Part of the amount from line 68370 on page 8 that is non-business income",
        "Part of the amount from line 68380 on page 8 that is non-business income",
        "× Amount from line number of your Form 428 shown in column 7 in Chart C on page 5",
    ):
        assert quoted in header, quoted


def test_the_line_49_header_states_the_half_up_cent_rule() -> None:
    header = dataset_header(LINE_49_ROUNDING, "ca-on").lower()

    assert "dollars-and-cents box" in header
    assert "half-up" in header
    assert "owner decided" in header or "owner's decision" in header


def test_line_49_is_the_credit_times_the_non_business_share_rounded_once() -> None:
    # 1905.46 × 30000 / 50000 = 1143.276, rounded half-up to the cent once.
    assert line_49("1905.46", "30000", "50000") == D("1143.28")
    assert line_49("1905.46", "40000", "50000") == D("1524.37")


def test_line_49_is_zero_when_there_is_no_non_business_income_from_foreign_sources() -> None:
    assert line_49("1905.46", "0", "0") == D("0.00")
