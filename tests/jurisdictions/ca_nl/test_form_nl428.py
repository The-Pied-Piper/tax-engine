"""The NL428 form declaration, loaded from the real part file beside a test header.

Form text (Form NL428, Newfoundland and Labrador Tax, CRA 5001-C 2025): line 105 "Line 105: Line 94
minus line 104 (if negative, enter "0") Enter this amount on line 42800 of your return.
Newfoundland and Labrador tax". The form is one form (lines 63 to 108) and exports line 105, the
Newfoundland and Labrador tax, and supplies line 105 as `ca/provincial_tax.amount`, the name the
federal T1 reads for line 42800. It also exports line 101 "Line 99 minus line 100 (if negative,
enter "0")" and line 104, which the return summary reads for the marginal tax rate.
The exports are declared as inputs of the test header: this test loads only the form declaration
(`nl428.yaml`), not the line parts, which have their own tests.
Lines 106 to 108 are deferred and are not declared here.
"""

from __future__ import annotations

from pathlib import Path

import tax_engine.jurisdictions.ca_nl
from tax_engine.adapters.outbound.yaml_jurisdictions import YamlJurisdictionSource
from tests.jurisdictions.ca_nl.support import (
    newfoundland_kinds,
    newfoundland_packages,
    newfoundland_units,
)

PART = Path(tax_engine.jurisdictions.ca_nl.__file__).parent / "manifests" / "2025" / "nl428.yaml"
LINE_101 = "ca-nl/nl428_line_101"
LINE_104 = "ca-nl/nl428_line_104"
LINE_105 = "ca-nl/nl428_newfoundland_and_labrador_tax_line_105"

HEADER = """\
jurisdiction: CA-NL
version: 1
valid_from_tax_year: 2025
inputs: []
outputs: []
capabilities: []
"""
# The inputs belong to the form that exports them, so they are declared in a part of that form.
OWNED_INPUTS = f"""\
form:
  name: ca-nl/nl428
inputs:
  - name: {LINE_101}
    required: true
  - name: {LINE_104}
    required: true
  - name: {LINE_105}
    required: true
"""


def test_the_form_is_declared_with_its_export_and_supply(tmp_path: Path) -> None:
    folder = tmp_path / "manifests" / "2025"
    folder.mkdir(parents=True)
    (folder / "00_header.yaml").write_text(HEADER, encoding="utf-8")
    (folder / "00_inputs.yaml").write_text(OWNED_INPUTS, encoding="utf-8")
    (folder / "01_nl428.yaml").write_text(PART.read_text(encoding="utf-8"), encoding="utf-8")
    source = YamlJurisdictionSource(
        newfoundland_packages().roots(),
        newfoundland_kinds(),
        newfoundland_units(),
    )

    manifest = source.load(folder)

    (nl428,) = (form for form in manifest.forms if form.name == "ca-nl/nl428")
    assert nl428.required is True
    assert nl428.title == "Form NL428: Newfoundland and Labrador Tax"
    assert tuple(nl428.exports) == (LINE_101, LINE_104, LINE_105)
    assert dict(nl428.supplies) == {"ca/provincial_tax.amount": LINE_105}
