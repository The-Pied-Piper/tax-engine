"""The 2025 `ca-qc/tp1_schedule_f_brackets` dataset, checked against Revenu Quebec Schedule F
(TP-1.D.F-V, 2025-12), Part B.

Form text: the two columns "If $63,060 or less" and "If more than $63,060"; in each, line 77 the
lower bound (18,130 00 and 63,060 00), the row "x 1%" and line 81 "+ 81 0 00 | 150 00".

Each bracket holds the form's column: its lower bound (line 77), its rate (the row "x 1%") and the
printed constant (line 81), carried as printed. The dataset has no rounding rule; the take-home
build rounds the dollars-and-cents boxes in its own part. The range starts above 18,130.00, so a
line 70 of $18,130 or less is outside it: Part B is not completed for it.
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
FAMILY = "ca-qc/tp1_schedule_f_brackets"
FORM = "Revenu Quebec TP-1.D.F-V (2025-12), Schedule F, Part B"


def _schedule() -> BracketSchedule:
    return SOURCE.get(FAMILY, 2025, BRACKETS).values


def test_2025_brackets_are_the_two_columns_as_printed() -> None:
    data = SOURCE.get(FAMILY, 2025, BRACKETS)

    assert [(b.lower, b.rate, b.tax_at_start) for b in data.values.brackets] == [
        (D("18130.00"), D("0.01"), D("0.00")),
        (D("63060.00"), D("0.01"), D("150.00")),
    ]


def test_2025_brackets_have_no_rounding_rule() -> None:
    data = SOURCE.get(FAMILY, 2025, BRACKETS)

    assert data.rounding == NO_ROUNDING
    assert data.values.tax_at_start_rounding == NO_ROUNDING


def test_2025_brackets_cite_the_schedule() -> None:
    assert SOURCE.get(FAMILY, 2025, BRACKETS).sources == (FORM,)


def test_2025_brackets_have_no_upper_end() -> None:
    assert _schedule().up_to is None


def test_the_range_starts_above_18130_and_not_at_it() -> None:
    schedule = _schedule()

    assert not schedule.covers(D("18130.00"))
    assert schedule.covers(D("18130.01"))


@pytest.mark.parametrize(
    ("amount", "lower"),
    [
        ("18130.01", "18130.00"),
        ("63060.00", "18130.00"),
        ("63060.01", "63060.00"),
        ("100000.00", "63060.00"),
    ],
)
def test_the_column_is_the_one_the_form_prints_for_the_amount(amount: str, lower: str) -> None:
    assert _schedule().column_for(D(amount)).lower == D(lower)
