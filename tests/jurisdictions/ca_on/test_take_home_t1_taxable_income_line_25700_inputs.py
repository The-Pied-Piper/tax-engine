"""The Ontario take-home manifest's T1 taxable income inputs a salary-only caller does not give:
lines 24400 to 25600, the ten lines that line 68 and line 25700 add.

T1 lines 58 to 67 (5006-R page 5): line 24400, 24900, 25000, 25100, 25200, 25300, 25395, 25400,
25500 and 25600. A salary-only caller has none of them, so each is an optional input left blank,
and the line 25700 part reads a blank as 0.

The real part is loaded under a test-local header, as the take-home header is another part's.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from tax_engine.adapters.outbound.yaml_jurisdictions import YamlJurisdictionSource
from tax_engine.domain.manifest import Manifest
from tax_engine.registrations import JURISDICTIONS, artifact_kinds, units
from tests.jurisdictions.ca_on.conftest import TakeHomeService
from tests.kinds import non_negative

PART = "t1_taxable_income_line_25700_inputs.yaml"
LINES = {
    "24400": ("58", "Canadian Armed Forces personnel and police deduction"),
    "24900": ("59", "Security options deductions"),
    "25000": ("60", "Other payments deduction"),
    "25100": ("61", "Limited partnership losses of other years"),
    "25200": ("62", "Non-capital losses of other years"),
    "25300": ("63", "Net capital losses of other years"),
    "25395": (
        "64",
        "Capital gains deduction for qualifying business transfers or qualifying cooperative "
        "conversions",
    ),
    "25400": ("65", "Capital gains deduction"),
    "25500": ("66", "Northern residents deductions"),
    "25600": ("67", "Additional deductions"),
}
NAMES = {line: f"ca/t1_line_{line}" for line in LINES}
HEADER = f"""\
jurisdiction: CA-ON
version: 1
valid_from_tax_year: 2025
outputs: [{", ".join(NAMES.values())}]
capabilities: []
"""
FORM = (
    "form:\n  name: ca/t1_taxable_income\n  required: true\n  exports:\n"
    + "".join(f"    - {name}\n" for name in NAMES.values())
    + "capabilities: []\n"
)


def _manifest(take_home_service: TakeHomeService, tmp_path: Path) -> Manifest:
    """The temporary take-home folder the shared builder writes, loaded as a manifest."""
    take_home_service(HEADER, FORM, PART)
    folder = tmp_path / "manifests" / "2025"
    return YamlJurisdictionSource(JURISDICTIONS.roots(), artifact_kinds(), units()).load(folder)


def test_the_part_declares_exactly_the_ten_lines(
    take_home_service: TakeHomeService, tmp_path: Path
) -> None:
    inputs = _manifest(take_home_service, tmp_path).inputs

    assert {name for name in inputs if name.startswith("ca/t1_line_")} == set(NAMES.values())


@pytest.mark.parametrize("line", LINES)
def test_a_request_that_leaves_out_the_line_is_read_as_blank(
    take_home_service: TakeHomeService, tmp_path: Path, line: str
) -> None:
    kinds = artifact_kinds()
    declaration = _manifest(take_home_service, tmp_path).inputs[NAMES[line]]
    default = declaration.default_artifact(kinds.kind(NAMES[line]))
    form_line, label = LINES[line]

    assert not declaration.required
    assert declaration.reference == line
    assert declaration.basis == f"Line {form_line} and line {line}: {label}."
    assert default is not None and default.is_blank
    assert non_negative(kinds.kind(NAMES[line]))
