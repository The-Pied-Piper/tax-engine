"""The MB479 form declaration, loaded from the real part file beside a test header.

Form text (Form MB479, Manitoba Credits, CRA 5007-TC): line 81 "Add lines 78 to 80. Enter this
amount on line 47900 of your return. Manitoba credits". The form exports line 81, the Manitoba
credits, and supplies line 81 as `ca/provincial_credits.amount`, the name the federal T1 reads for
line 47900. Line 81 is declared as an input of the test header: this test loads only the form
declaration (`mb479.yaml`), not the line parts, which have their own tests.
"""

from __future__ import annotations

from pathlib import Path

import tax_engine.jurisdictions.ca_mb
from tax_engine.adapters.outbound.yaml_jurisdictions import YamlJurisdictionSource
from tests.jurisdictions.ca_mb.support import (
    manitoba_kinds,
    manitoba_packages,
    manitoba_units,
)

PART = Path(tax_engine.jurisdictions.ca_mb.__file__).parent / "manifests" / "2025" / "mb479.yaml"
LINE_81 = "ca-mb/mb479_manitoba_credits_line_81"

HEADER = f"""\
jurisdiction: CA-MB
version: 1
valid_from_tax_year: 2025
inputs: []
outputs:
  - {LINE_81}
capabilities: []
"""
# The inputs belong to the form that exports them, so they are declared in a part of that form.
OWNED_INPUTS = f"""\
form:
  name: ca-mb/mb479
inputs:
  - name: {LINE_81}
    required: true
"""


def test_the_form_is_declared_with_its_export_and_its_supply(tmp_path: Path) -> None:
    folder = tmp_path / "manifests" / "2025"
    folder.mkdir(parents=True)
    (folder / "00_header.yaml").write_text(HEADER, encoding="utf-8")
    (folder / "00_inputs.yaml").write_text(OWNED_INPUTS, encoding="utf-8")
    (folder / "01_mb479.yaml").write_text(PART.read_text(encoding="utf-8"), encoding="utf-8")
    source = YamlJurisdictionSource(
        manitoba_packages().roots(),
        manitoba_kinds(),
        manitoba_units(),
    )

    manifest = source.load(folder)

    (mb479,) = (form for form in manifest.forms if form.name == "ca-mb/mb479")
    assert mb479.required is True
    assert mb479.title == "Form MB479: Manitoba Credits"
    assert tuple(mb479.exports) == (LINE_81,)
    assert dict(mb479.supplies) == {"ca/provincial_credits.amount": LINE_81}
