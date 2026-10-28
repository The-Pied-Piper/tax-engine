"""ON479-A's rate table, shared by the ca-on capability tests of lines 7 and 8.

The "Family adjusted income and Tax credit rate" table copied row for row from
`docs/cra-forms-2025/5006-tca-25e.txt`, the 9% row as printed ("more than $132,000 but not more
than $136,500: 9%", overlapping "more than $135,600 but not more than $139,200: 7%"), read for a
made-up family income kind from a made-up dataset family.
"""

from __future__ import annotations

from decimal import Decimal

from tax_calculator.domain.artifact import ArtifactKind
from tax_calculator.domain.parameters.datasets import ParameterDataset
from tax_calculator.domain.parameters.rate import Rate
from tax_calculator.domain.parameters.rate_table import RATE_TABLE, RateTable, RateTableRow
from tax_calculator.domain.parameters.rounding import NO_ROUNDING, RoundingRule

D = Decimal

FAMILY_INCOME = ArtifactKind("ex/family_adjusted_income", Decimal)

# (more than, not more than, rate), as printed: "more than $0 but not more than $20,000: 75%", ...
ON479A_ROWS: tuple[tuple[str, str | None, str], ...] = (
    ("0", "20000", "0.75"),
    ("20000", "22500", "0.73"),
    ("22500", "25000", "0.71"),
    ("25000", "27500", "0.69"),
    ("27500", "30000", "0.67"),
    ("30000", "32500", "0.65"),
    ("32500", "35000", "0.63"),
    ("35000", "37500", "0.61"),
    ("37500", "40000", "0.59"),
    ("40000", "45000", "0.57"),
    ("45000", "50000", "0.55"),
    ("50000", "55000", "0.53"),
    ("55000", "60000", "0.51"),
    ("60000", "63600", "0.49"),
    ("63600", "67200", "0.47"),
    ("67200", "70800", "0.45"),
    ("70800", "74400", "0.43"),
    ("74400", "78000", "0.41"),
    ("78000", "81600", "0.39"),
    ("81600", "85200", "0.37"),
    ("85200", "88800", "0.35"),
    ("88800", "92400", "0.33"),
    ("92400", "96000", "0.31"),
    ("96000", "99600", "0.29"),
    ("99600", "103200", "0.27"),
    ("103200", "106800", "0.25"),
    ("106800", "110400", "0.23"),
    ("110400", "114000", "0.21"),
    ("114000", "117600", "0.19"),
    ("117600", "121200", "0.17"),
    ("121200", "124800", "0.15"),
    ("124800", "128400", "0.13"),
    ("128400", "132000", "0.11"),
    ("132000", "136500", "0.09"),  # CRA's typo, as printed: the next row starts at 135,600
    ("135600", "139200", "0.07"),
    ("139200", "142800", "0.05"),
    ("142800", "146400", "0.03"),
    ("146400", "150000", "0.01"),
    ("150000", None, "0"),
)


def form_row(more_than: str, not_more_than: str | None, rate: str) -> RateTableRow:
    upper = None if not_more_than is None else D(not_more_than)
    return RateTableRow(D(more_than), upper, Rate(D(rate)))


def on479a_table() -> RateTable:
    """Line 7's "enter 75%" for 0, then the form's 39 rows, the last one open-ended."""
    return RateTable(Rate(D("0.75")), tuple(form_row(*printed) for printed in ON479A_ROWS))


def table(
    values: RateTable | None = None, rounding: RoundingRule = NO_ROUNDING
) -> ParameterDataset[RateTable]:
    return ParameterDataset(
        "ex/care_rate_table",
        2025,
        RATE_TABLE,
        values or on479a_table(),
        rounding,
        ("docs/cra-forms-2025/5006-tca-25e.txt",),
    )
