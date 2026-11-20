"""The 2025 `ca-qc/schedule_k_brackets` dataset, checked against Revenu Quebec Schedule K
(TP-1.D.K-V, 2025-12), Part C, table "Individual without a spouse on December 31".

Form text: column A for a line 48 of $5,000 or less and column B for more than $5,000; in each, line
78 the lower bound (0,000 00 and 5,000 00), line 80 the rate (7.84% and 11.76%) and line 82 the
constant (000 00 and 392 00).

Each bracket holds the form's column: its lower bound (line 78), its rate (line 80) and the printed
constant (line 82), carried as printed. The dataset has no rounding rule; the take-home build
rounds the dollars-and-cents boxes in its own parts. Column A starts at 0 itself, so a line 48 of 0
is covered, and column B has no upper end.
"""

from __future__ import annotations

from decimal import Decimal

import pytest

from tax_engine.adapters.outbound.yaml_parameters import YamlParameterSource
from tax_engine.domain.parameters.brackets import BRACKETS, BracketSchedule
from tax_engine.domain.parameters.rounding import NO_ROUNDING
from tests.jurisdictions.ca_qc.support import quebec_packages, quebec_parameter_parsers

D = Decimal
# Quebec is not in `registrations.JURISDICTIONS` yet, so the source is built over its own packages.
SOURCE = YamlParameterSource(quebec_packages().roots(), quebec_parameter_parsers())
FAMILY = "ca-qc/schedule_k_brackets"
FORM = "Revenu Quebec TP-1.D.K-V (2025-12), Schedule K, Part C"


def _schedule() -> BracketSchedule:
    return SOURCE.get(FAMILY, 2025, BRACKETS).values


def test_2025_brackets_are_the_two_columns_as_printed() -> None:
    data = SOURCE.get(FAMILY, 2025, BRACKETS)

    assert [(b.lower, b.rate, b.tax_at_start) for b in data.values.brackets] == [
        (D("0"), D("0.0784"), D("0.00")),
        (D("5000"), D("0.1176"), D("392.00")),
    ]


def test_2025_brackets_have_no_rounding_rule() -> None:
    data = SOURCE.get(FAMILY, 2025, BRACKETS)

    assert data.rounding == NO_ROUNDING
    assert data.values.tax_at_start_rounding == NO_ROUNDING


def test_2025_brackets_cite_the_schedule() -> None:
    assert SOURCE.get(FAMILY, 2025, BRACKETS).sources == (FORM,)


def test_2025_brackets_have_no_upper_end() -> None:
    assert _schedule().up_to is None


def test_the_range_starts_at_zero() -> None:
    assert _schedule().covers(D("0.00"))


@pytest.mark.parametrize(
    ("amount", "lower"),
    [
        ("0.00", "0"),
        ("5000.00", "0"),
        ("5000.01", "5000"),
        ("14669.00", "5000"),
        ("20000.00", "5000"),
    ],
)
def test_the_column_is_the_one_the_form_prints_for_the_amount(amount: str, lower: str) -> None:
    assert _schedule().column_for(D(amount)).lower == D(lower)
