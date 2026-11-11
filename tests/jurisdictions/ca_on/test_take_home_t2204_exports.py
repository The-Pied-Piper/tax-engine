"""The Ontario take-home T2204 form part exports exactly three figures, computed through the engine.

The real `t2204.yaml` form part names the form and its exports. The return reads three figures from
it: line 4, the total premiums deducted (`ca/t2204_premiums_deducted`), the overpayment refunded on
T1 line 45000 (`ca/ei_overpayment`) and line 16, the amount entered on T1 line 31200
(`ca/t2204_line_16`). Lines 15 and its count are no longer exported. The test composes the real form
part with the real inputs part and the real line parts under a test-local header that declares the
salary, the one input a salary-only caller gives.
"""

from __future__ import annotations

from decimal import Decimal
from pathlib import Path

import pytest

from tax_engine.adapters.outbound.yaml_jurisdictions import YamlJurisdictionSource
from tax_engine.domain.artifact import Artifact, ArtifactRegistry
from tax_engine.domain.jurisdiction_code import JurisdictionCode
from tax_engine.domain.worksheet import Worksheet
from tax_engine.registrations import JURISDICTIONS, artifact_kinds
from tests.jurisdictions.ca_on.conftest import TAKE_HOME, TakeHomeService
from tests.kinds import bundled_kinds

D = Decimal
CODE = JurisdictionCode("CA-ON")
SALARY = "ca/employment_income"
LINE_4_GIVEN = "ca/t2204_premiums_deducted_given"
LINE_4 = "ca/t2204_premiums_deducted"
OVERPAYMENT = "ca/ei_overpayment"
LINE_16 = "ca/t2204_line_16"
FORM = next(TAKE_HOME.rglob("t2204.yaml")).read_text(encoding="utf-8")
PARTS = (
    "t2204_inputs.yaml",
    "t2204_line_1.yaml",
    "t2204_line_3.yaml",
    "t2204_line_4.yaml",
    "t2204_line_6.yaml",
    "t2204_line_7.yaml",
    "t2204_line_8.yaml",
    "t2204_line_10.yaml",
    "t2204_line_13.yaml",
    "t2204_line_14.yaml",
    "t2204_line_15.yaml",
    "t2204_line_16.yaml",
)
HEADER = f"""\
jurisdiction: CA-ON
version: 1
valid_from_tax_year: 2025
inputs:
  - name: {SALARY}
    required: true
outputs:
  - {SALARY}
capabilities: []
"""


def _worksheet(
    take_home_service: TakeHomeService, salary: str, line_4_given: str | None
) -> tuple[ArtifactRegistry, Worksheet]:
    kinds = bundled_kinds()
    starting = [Artifact(kinds.kind(SALARY), D(salary))]
    if line_4_given is not None:
        starting.append(Artifact(kinds.kind(LINE_4_GIVEN), D(line_4_given)))
    service = take_home_service(HEADER, FORM, *PARTS)
    return kinds, service.compute(CODE, 2025, *starting)["ca/t2204"][0]


def test_the_form_exports_exactly_the_three_figures(
    take_home_service: TakeHomeService, tmp_path: Path
) -> None:
    take_home_service(HEADER, FORM, *PARTS)
    folder = tmp_path / "manifests" / "2025"
    manifest = YamlJurisdictionSource(JURISDICTIONS.roots(), artifact_kinds()).load(folder)
    (worksheet,) = [form for form in manifest.forms if form.name == "ca/t2204"]
    assert worksheet.exports == (LINE_4, OVERPAYMENT, LINE_16)


@pytest.mark.parametrize(
    ("salary", "line_4_given", "line_4", "overpayment", "line_16"),
    [
        # A $70,000 salary: premiums at the 1,077.48 cap, no overpayment.
        ("70000", None, "1077.48", "0", "1077.48"),
        # A $2,010 salary: line 4 is 32.96 but line 16 is 10.00, so 22.96 is refunded.
        ("2010", None, "32.96", "22.96", "10.00"),
        # Line 4 given above the cap at $70,000: line 16 stays at the cap, the excess is refunded.
        ("70000", "1148.00", "1148.00", "70.52", "1077.48"),
    ],
)
def test_the_exports_carry_line_4_the_overpayment_and_line_16(
    take_home_service: TakeHomeService,
    salary: str,
    line_4_given: str | None,
    line_4: str,
    overpayment: str,
    line_16: str,
) -> None:
    kinds, worksheet = _worksheet(take_home_service, salary, line_4_given)
    assert worksheet.get(kinds.kind(LINE_4)).value == D(line_4)
    assert worksheet.get(kinds.kind(OVERPAYMENT)).value == D(overpayment)
    assert worksheet.get(kinds.kind(LINE_16)).value == D(line_16)
