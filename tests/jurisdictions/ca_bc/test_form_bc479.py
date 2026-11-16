"""The BC479 form declaration, loaded from the real part file beside a test header.

Form text (Form BC479, British Columbia Credits, CRA 5010-TC): line 45 "Line 36 plus line 44
Enter this amount on line 47900 of your return. British Columbia credits". The form is one form
(lines 1 to 45) and exports line 45, the British Columbia credits, and supplies line 45 as
`ca/provincial_credits.amount`, the name the federal T1 reads for line 47900. Line 45 is
declared as an input of the test header: this test loads only the form declaration (`bc479.yaml`),
not the line parts, which have their own tests.
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

PART = Path(tax_engine.jurisdictions.ca_bc.__file__).parent / "manifests" / "2025" / "bc479.yaml"
LINE_45 = "ca-bc/bc479_british_columbia_credits_line_45"

HEADER = f"""\
jurisdiction: CA-BC
version: 1
valid_from_tax_year: 2025
inputs:
  - name: {LINE_45}
    required: true
outputs:
  - {LINE_45}
capabilities: []
"""


def test_the_form_is_declared_with_its_export_and_its_supply(tmp_path: Path) -> None:
    folder = tmp_path / "manifests" / "2025"
    folder.mkdir(parents=True)
    (folder / "00_header.yaml").write_text(HEADER, encoding="utf-8")
    (folder / "01_bc479.yaml").write_text(PART.read_text(encoding="utf-8"), encoding="utf-8")
    source = YamlJurisdictionSource(
        british_columbia_packages().roots(),
        british_columbia_kinds(),
        british_columbia_units(),
    )

    manifest = source.load(folder)

    (bc479,) = (form for form in manifest.forms if form.name == "ca-bc/bc479")
    assert bc479.required is True
    assert bc479.title == "Form BC479: British Columbia Credits"
    assert tuple(bc479.exports) == (LINE_45,)
    assert dict(bc479.supplies) == {"ca/provincial_credits.amount": LINE_45}
