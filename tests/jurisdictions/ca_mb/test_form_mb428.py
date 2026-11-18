"""The MB428 form declaration, loaded from the real part file beside a test header.

Form text (Form MB428, Manitoba Tax, CRA 5007-C): line 82 "Enter this amount on line 42800 of your
return." The form is one form (lines 58 to 82) and exports line 65, the tax after the credits
("Line 60 minus line 64 (if negative, enter "0")", which the return summary reads for the marginal
tax rate), and line 82, the Manitoba tax, and supplies line 82 as `ca/provincial_tax.amount`, the
name the federal T1 reads for line 42800. Lines 65 and 82 are declared as inputs of the test header:
this test loads only the form declaration (`mb428.yaml`), not the line parts, which have their own
tests.
"""

from __future__ import annotations

from pathlib import Path

import tax_engine.jurisdictions.ca_mb
from tax_engine.adapters.outbound.yaml_jurisdictions import YamlJurisdictionSource
from tests.jurisdictions.ca_mb.support import manitoba_kinds, manitoba_packages, manitoba_units

PART = Path(tax_engine.jurisdictions.ca_mb.__file__).parent / "manifests" / "2025" / "mb428.yaml"
LINE_82 = "ca-mb/mb428_manitoba_tax_line_82"
LINE_65 = "ca-mb/mb428_tax_after_credits_line_65"

HEADER = f"""\
jurisdiction: CA-MB
version: 1
valid_from_tax_year: 2025
inputs:
  - name: {LINE_65}
    required: true
  - name: {LINE_82}
    required: true
outputs:
  - {LINE_82}
capabilities: []
"""


def test_the_form_is_declared_with_its_export_and_supply(tmp_path: Path) -> None:
    folder = tmp_path / "manifests" / "2025"
    folder.mkdir(parents=True)
    (folder / "00_header.yaml").write_text(HEADER, encoding="utf-8")
    (folder / "01_mb428.yaml").write_text(PART.read_text(encoding="utf-8"), encoding="utf-8")
    source = YamlJurisdictionSource(
        manitoba_packages().roots(),
        manitoba_kinds(),
        manitoba_units(),
    )

    manifest = source.load(folder)

    (mb428,) = (form for form in manifest.forms if form.name == "ca-mb/mb428")
    assert mb428.required is True
    assert mb428.title == "Form MB428: Manitoba Tax"
    assert tuple(mb428.exports) == (LINE_65, LINE_82)
    assert dict(mb428.supplies) == {"ca/provincial_tax.amount": LINE_82}
