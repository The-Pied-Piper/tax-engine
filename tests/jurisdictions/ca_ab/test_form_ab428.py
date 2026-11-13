"""The AB428 form declaration, loaded from the real part file beside a test header.

Form text (Form AB428, CRA 5009-c-25e.txt): "Line 75: Line 73 minus line 74 (if negative, enter "0")
Enter this amount on line 42800 of your return. Alberta tax =".
The form exports line 75 and supplies it as `ca/provincial_tax.amount`, the name the federal T1
reads for line 42800. Line 75 is declared as an input of the test header: this test loads only
the form declaration (`ab428.yaml`), not the step of `ab428_line_75.yaml`, which has its own test.
"""

from __future__ import annotations

from pathlib import Path

import tax_engine.jurisdictions.ca_ab
from tax_engine.adapters.outbound.yaml_jurisdictions import YamlJurisdictionSource
from tests.jurisdictions.ca_ab.support import alberta_kinds, alberta_packages, alberta_units

PART = Path(tax_engine.jurisdictions.ca_ab.__file__).parent / "manifests" / "2025" / "ab428.yaml"
LINE_75 = "ca-ab/ab428_alberta_tax_line_75"

HEADER = f"""\
jurisdiction: CA-AB
version: 1
valid_from_tax_year: 2025
inputs:
  - name: {LINE_75}
    required: true
outputs:
  - {LINE_75}
capabilities: []
"""


def test_the_form_is_declared_with_its_export_and_supply(tmp_path: Path) -> None:
    folder = tmp_path / "manifests" / "2025"
    folder.mkdir(parents=True)
    (folder / "00_header.yaml").write_text(HEADER, encoding="utf-8")
    (folder / "01_ab428.yaml").write_text(PART.read_text(encoding="utf-8"), encoding="utf-8")
    source = YamlJurisdictionSource(alberta_packages().roots(), alberta_kinds(), alberta_units())

    manifest = source.load(folder)

    (ab428,) = (form for form in manifest.forms if form.name == "ca-ab/ab428")
    assert ab428.required is True
    assert ab428.title == "Form AB428: Alberta Tax and Credits"
    assert tuple(ab428.exports) == (LINE_75,)
    assert dict(ab428.supplies) == {"ca/provincial_tax.amount": LINE_75}
