"""The 2026 datasets of the TP-752.PC-V "Tax Credit for Career Extension" lines, against the printed
form (Revenu Quebec TP-752.PC-V, 2026-10).

Line 15 "- 15 7,655 00"; line 16 "Subtract $7,655 from line 14 (maximum $12,755)."; line 35 "x 14%
Multiply line 16 by 14%."; line 37 "- 37 57,660 00"; line 39 "x 7% Multiply line 38 by 7%."; line 48
"Add lines 359 through 367 of your return. x 14%".
The two printed amounts (lines 15 and 37) are held as printed and claimed whole (the `credit` kind),
the maximum of line 16 is the `amount` kind and the three printed percentages are `rate`s (0.14,
0.07 and 0.14). Each is a dollars-and-cents figure or line, so it rounds half-up to the cent, the
project's choice, as the form states no rounding rule. The 2026-10 edition is published, so unlike
the other 2026 files these are not provisional.
One module per year for the six families (the dataset shape test of each is the same); the existence
of every 2026 file is also pinned by `test_every_family_has_2026.py`.
"""

from __future__ import annotations

from decimal import Decimal
from pathlib import Path
from typing import Any

import pytest

import tax_engine.jurisdictions.ca_qc as ca_qc_package
from tax_engine.adapters.outbound.yaml_parameters import YamlParameterSource
from tax_engine.domain.parameters.amount import AMOUNT, Amount
from tax_engine.domain.parameters.credit import CREDIT, Credit
from tax_engine.domain.parameters.kind import ParameterKind
from tax_engine.domain.parameters.rate import RATE, Rate
from tax_engine.domain.parameters.rounding import RoundingMode, RoundTo
from tests.jurisdictions.ca_qc.support import (
    quebec_packages,
    quebec_parameter_parsers,
    quebec_units,
)

D = Decimal
YEAR = 2026
SOURCE = YamlParameterSource(quebec_packages().roots(), quebec_parameter_parsers(), quebec_units())
SOURCE_FORM = "Revenu Quebec TP-752.PC-V (2026-10)"
CASES = [
    ("ca-qc/tp752_pc_line_15", CREDIT, Credit(amount=D("7655"))),
    ("ca-qc/tp752_pc_line_16_maximum", AMOUNT, Amount(D("12755"))),
    ("ca-qc/tp752_pc_line_35_rate", RATE, Rate(D("0.14"))),
    ("ca-qc/tp752_pc_line_37", CREDIT, Credit(amount=D("57660"))),
    ("ca-qc/tp752_pc_line_39_rate", RATE, Rate(D("0.07"))),
    ("ca-qc/tp752_pc_line_48_rate", RATE, Rate(D("0.14"))),
]


@pytest.mark.parametrize(("family", "kind", "values"), CASES)
def test_2026_the_figure_is_the_printed_one(
    family: str, kind: ParameterKind[Any], values: object
) -> None:
    data: Any = SOURCE.get(family, YEAR, kind)

    assert data.values == values


@pytest.mark.parametrize(("family", "kind", "values"), CASES)
def test_2026_the_figure_rounds_half_up_to_the_cent_and_cites_the_form(
    family: str, kind: ParameterKind[Any], values: object
) -> None:
    data: Any = SOURCE.get(family, YEAR, kind)

    assert data.rounding == RoundTo(D("0.01"), RoundingMode.HALF_UP)
    assert data.sources == (SOURCE_FORM,)


@pytest.mark.parametrize("family", [family for family, _, _ in CASES])
def test_2026_file_is_printed_on_the_2026_edition_so_it_is_not_provisional(family: str) -> None:
    path = Path(ca_qc_package.__file__).parent / "parameters" / family.split("/")[1] / "2026.yaml"

    assert not path.read_text().startswith("# Provisional")
