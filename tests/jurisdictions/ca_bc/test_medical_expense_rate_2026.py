"""The 2026 `ca-bc/medical_expense_rate` dataset: 3%, printed on Form BC428 line 48 (CRA 5010).
It is a dollars-and-cents or rate figure, so it rounds half-up to the cent, the project's
choice, as the form states no rounding rule. Provisional: the 2026 form is not published, so
the 2025 figure is carried forward.
"""

from __future__ import annotations

from decimal import Decimal

from tax_engine.adapters.outbound.yaml_parameters import YamlParameterSource
from tax_engine.domain.parameters.rate import RATE, Rate
from tax_engine.domain.parameters.rounding import RoundingMode, RoundTo
from tax_engine.domain.registry import Namespace
from tests.jurisdictions.ca_bc.support import (
    british_columbia_packages,
    british_columbia_parameter_parsers,
    british_columbia_units,
)

D = Decimal
FAMILY = "ca-bc/medical_expense_rate"
SOURCE = YamlParameterSource(
    british_columbia_packages().roots(),
    british_columbia_parameter_parsers(),
    british_columbia_units(),
)


def test_2026_figure_is_0_03() -> None:
    data = SOURCE.get(FAMILY, 2026, RATE)

    assert data.values == Rate(D("0.03"))
    assert data.rounding == RoundTo(D("0.01"), RoundingMode.HALF_UP)
    assert data.tax_year == 2026


def test_the_2026_file_is_provisional_and_states_its_derivation() -> None:
    root = british_columbia_packages().roots()[Namespace("ca-bc")]
    lines = (root / "parameters" / FAMILY.split("/")[1] / "2026.yaml").read_text().splitlines()

    assert lines[0] == (
        "# Provisional: taken from the 2025 form text named in sources; to be confirmed against "
        "the 2026 form text when CRA publishes it."
    )
    assert lines[1] == (
        "# Derivation: carried forward unchanged from the 2025 file; the 2026 form is not yet "
        "published."
    )


def test_2026_is_carried_forward_unchanged_from_2025() -> None:
    assert SOURCE.get(FAMILY, 2026, RATE).values == SOURCE.get(FAMILY, 2025, RATE).values
