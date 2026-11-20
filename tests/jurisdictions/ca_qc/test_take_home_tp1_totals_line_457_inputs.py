"""TP-1 (2025) line 457, the two Schedule L amounts the guide totals against $2,000: net business
income (Schedule L line 27) and the insurable earnings of a family-type resource (Schedule L line
40). The take-home gives neither, so each is an optional input; a blank is read as 0 by line 457.
The real part is loaded under a test-local header and form declaration over the Quebec package list
of `support.py`."""

from __future__ import annotations

from pathlib import Path

import pytest

from tax_engine.adapters.outbound.yaml_jurisdictions import YamlJurisdictionSource
from tax_engine.domain.manifest import Manifest
from tests.jurisdictions.ca_qc.conftest import TakeHomeService
from tests.jurisdictions.ca_qc.support import quebec_kinds, quebec_packages, quebec_units
from tests.kinds import non_negative

PART = "tp1_totals_line_457_inputs.yaml"
# Each input: its reference and the printed words it is taken from (the guide, line 457).
INPUTS = {
    "ca-qc/tp1_net_business_income_schedule_l_line_27": (
        "Schedule L, line 27",
        "your net business income",
    ),
    "ca-qc/tp1_family_resource_earnings_schedule_l_line_40": (
        "Schedule L, line 40",
        "your insurable earnings as a person responsible for a family-type resource or an "
        "intermediate resource",
    ),
}
HEADER = f"""\
jurisdiction: CA-QC
version: 1
valid_from_tax_year: 2025
outputs: [{", ".join(INPUTS)}]
capabilities: []
"""
FORM = (
    "form:\n  name: ca-qc/tp1_totals\n  required: true\n  exports:\n"
    + "".join(f"    - {name}\n" for name in INPUTS)
    + "capabilities: []\n"
)


def _manifest(take_home_service: TakeHomeService, tmp_path: Path) -> Manifest:
    take_home_service(HEADER, FORM, PART)
    folder = tmp_path / "manifests" / "2025"
    return YamlJurisdictionSource(quebec_packages().roots(), quebec_kinds(), quebec_units()).load(
        folder
    )


def test_the_part_declares_exactly_the_two_schedule_l_amounts(
    take_home_service: TakeHomeService, tmp_path: Path
) -> None:
    inputs = _manifest(take_home_service, tmp_path).inputs

    assert set(inputs) == set(INPUTS)


@pytest.mark.parametrize("name", list(INPUTS))
def test_a_request_that_leaves_out_the_amount_is_read_as_blank(
    take_home_service: TakeHomeService, tmp_path: Path, name: str
) -> None:
    declaration = _manifest(take_home_service, tmp_path).inputs[name]
    default = declaration.default_artifact(quebec_kinds().kind(name))

    assert not declaration.required
    assert declaration.reference == INPUTS[name][0]
    assert declaration.basis == INPUTS[name][1]
    assert default is not None and default.is_blank


@pytest.mark.parametrize("name", list(INPUTS))
def test_the_input_kind_is_registered_and_non_negative(name: str) -> None:
    assert non_negative(quebec_kinds().kind(name)) is True
