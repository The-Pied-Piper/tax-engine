"""The 2026 `ca-qc/tp752_pc_line_37` dataset (TP-752.PC-V, Tax Credit for Career Extension).
Revenu Quebec TP-752.PC-V (2026-10), line 37 "- 37 57,660 00". It is a credit figure, held as
printed; the line is a
dollars-and-cents line, so the figure rounds half-up to the cent, the project's choice, as the form
states no rounding rule. The 2026-10 edition is published, so unlike the other 2026 files this one
is not provisional.
"""

from __future__ import annotations

from decimal import Decimal
from pathlib import Path

import tax_engine.jurisdictions.ca_qc as ca_qc_package
from tax_engine.adapters.outbound.yaml_parameters import YamlParameterSource
from tax_engine.domain.parameters.credit import CREDIT, Credit
from tax_engine.domain.parameters.rounding import RoundingMode, RoundTo
from tests.jurisdictions.ca_qc.support import (
    quebec_packages,
    quebec_parameter_parsers,
    quebec_units,
)

D = Decimal
SOURCE = YamlParameterSource(quebec_packages().roots(), quebec_parameter_parsers(), quebec_units())
FAMILY = "ca-qc/tp752_pc_line_37"
SOURCE_FORM = "Revenu Quebec TP-752.PC-V (2026-10)"


def test_2026_the_figure_is_the_printed_one() -> None:
    data = SOURCE.get(FAMILY, 2026, CREDIT)

    assert data.values == Credit(amount=D("57660"))


def test_2026_the_figure_rounds_half_up_to_the_cent() -> None:
    data = SOURCE.get(FAMILY, 2026, CREDIT)

    assert data.rounding == RoundTo(D("0.01"), RoundingMode.HALF_UP)


def test_2026_the_figure_cites_the_form() -> None:
    data = SOURCE.get(FAMILY, 2026, CREDIT)

    assert data.sources == (SOURCE_FORM,)


def test_2026_file_is_printed_on_the_2026_edition_so_it_is_not_provisional() -> None:
    path = Path(ca_qc_package.__file__).parent / "parameters" / "tp752_pc_line_37" / "2026.yaml"

    assert not path.read_text().startswith("# Provisional")
