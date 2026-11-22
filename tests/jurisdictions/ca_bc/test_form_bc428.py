"""The BC428 form declaration, loaded from the real part file beside a test header.

Form text (Form BC428, British Columbia Tax, CRA 5010-C): line 91 "Enter this amount on line
42800 of your return." The form is one form (lines 1 to 91) and exports line 91, the British
Columbia tax, and supplies line 91 as `ca/provincial_tax.amount`, the name the federal T1 reads for
line 42800. It also exports the figures the return summary reads for the marginal tax rate: the
bracket rate of line 5 and of line 12 (one of them blank), the tax reduction's line 78 ("Line 76
multiplied by the percentage from line 77"), line 79 ("British Columbia tax reduction") and line
80 ("Line 72 minus line 79 (if negative, enter "0")"). Each export is declared as an input of the
test header: this test loads only the form declaration (`bc428.yaml`), not the line parts, which
have their own tests.
"""

from __future__ import annotations

from pathlib import Path

import tax_engine.jurisdictions.ca_bc
from tax_engine.adapters.outbound.yaml_jurisdictions import YamlJurisdictionSource
from tests.jurisdictions.ca_bc.support import (
    british_columbia_kinds,
    british_columbia_packages,
    british_columbia_units,
)

PART = Path(tax_engine.jurisdictions.ca_bc.__file__).parent / "manifests" / "2025" / "bc428.yaml"
LINE_5 = "ca-bc/bc428_bracket_rate_line_5"
LINE_12 = "ca-bc/bc428_bracket_rate_line_12"
LINE_78 = "ca-bc/bc428_reduction_clawback_line_78"
LINE_79 = "ca-bc/bc428_british_columbia_tax_reduction_line_79"
LINE_80 = "ca-bc/bc428_tax_after_reduction_line_80"
LINE_91 = "ca-bc/bc428_british_columbia_tax_line_91"

HEADER = """\
jurisdiction: CA-BC
version: 1
valid_from_tax_year: 2025
inputs: []
outputs: []
capabilities: []
"""
# The inputs belong to the form that exports them, so they are declared in a part of that form.
OWNED_INPUTS = f"""\
form:
  name: ca-bc/bc428
inputs:
  - name: {LINE_5}
    required: true
  - name: {LINE_12}
    required: true
  - name: {LINE_78}
    required: true
  - name: {LINE_79}
    required: true
  - name: {LINE_80}
    required: true
  - name: {LINE_91}
    required: true
"""


def test_the_form_is_declared_with_its_export_and_supply(tmp_path: Path) -> None:
    folder = tmp_path / "manifests" / "2025"
    folder.mkdir(parents=True)
    (folder / "00_header.yaml").write_text(HEADER, encoding="utf-8")
    (folder / "00_inputs.yaml").write_text(OWNED_INPUTS, encoding="utf-8")
    (folder / "01_bc428.yaml").write_text(PART.read_text(encoding="utf-8"), encoding="utf-8")
    source = YamlJurisdictionSource(
        british_columbia_packages().roots(),
        british_columbia_kinds(),
        british_columbia_units(),
    )

    manifest = source.load(folder)

    (bc428,) = (form for form in manifest.forms if form.name == "ca-bc/bc428")
    assert bc428.required is True
    assert bc428.title == "Form BC428: British Columbia Tax"
    assert tuple(bc428.exports) == (LINE_5, LINE_12, LINE_78, LINE_79, LINE_80, LINE_91)
    assert dict(bc428.supplies) == {"ca/provincial_tax.amount": LINE_91}
