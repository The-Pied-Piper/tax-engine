"""The BC428 form declaration, loaded from the real part file beside a test header.

Form text (Form BC428, British Columbia Tax, CRA 5010-C): line 91 "Enter this amount on line
42800 of your return." The form is one form (lines 1 to 91) and exports line 91, the British
Columbia tax, and supplies line 91 as `ca/provincial_tax.amount`, the name the federal T1 reads for
line 42800. Line 91 is declared as an input of the test header: this test loads only the form
declaration (`bc428.yaml`), not the line parts, which have their own tests.
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
LINE_91 = "ca-bc/bc428_british_columbia_tax_line_91"

HEADER = f"""\
jurisdiction: CA-BC
version: 1
valid_from_tax_year: 2025
inputs:
  - name: {LINE_91}
    required: true
outputs:
  - {LINE_91}
capabilities: []
"""


def test_the_form_is_declared_with_its_export_and_supply(tmp_path: Path) -> None:
    folder = tmp_path / "manifests" / "2025"
    folder.mkdir(parents=True)
    (folder / "00_header.yaml").write_text(HEADER, encoding="utf-8")
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
    assert tuple(bc428.exports) == (LINE_91,)
    assert dict(bc428.supplies) == {"ca/provincial_tax.amount": LINE_91}
