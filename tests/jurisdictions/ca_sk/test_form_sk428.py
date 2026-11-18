"""The SK428 form declaration, loaded from the real part file beside a test header.

Form text (Form SK428, Saskatchewan Tax, CRA 5008-C): line 82 "Enter this amount on line 42800 of
your return." The form is one form (lines 58 to 82) and exports line 82, the Saskatchewan tax, and
supplies line 82 as `ca/provincial_tax.amount`, the name the federal T1 reads for line 42800. The
form also exports line 67, "Line 62 minus line 66 (if negative, enter "0")", the figure the return
summary reads for the marginal tax rate. Each export is declared as an input of the test header:
this test loads only the form declaration (`sk428.yaml`), not the line parts, which have their own
tests.
"""

from __future__ import annotations

from pathlib import Path

import tax_engine.jurisdictions.ca_sk
from tax_engine.adapters.outbound.yaml_jurisdictions import YamlJurisdictionSource
from tests.jurisdictions.ca_sk.support import (
    saskatchewan_kinds,
    saskatchewan_packages,
    saskatchewan_units,
)

PART = Path(tax_engine.jurisdictions.ca_sk.__file__).parent / "manifests" / "2025" / "sk428.yaml"
LINE_67 = "ca-sk/sk428_tax_after_credits_line_67"
LINE_82 = "ca-sk/sk428_saskatchewan_tax_line_82"

HEADER = f"""\
jurisdiction: CA-SK
version: 1
valid_from_tax_year: 2025
inputs:
  - name: {LINE_67}
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
    (folder / "01_sk428.yaml").write_text(PART.read_text(encoding="utf-8"), encoding="utf-8")
    source = YamlJurisdictionSource(
        saskatchewan_packages().roots(),
        saskatchewan_kinds(),
        saskatchewan_units(),
    )

    manifest = source.load(folder)

    (sk428,) = (form for form in manifest.forms if form.name == "ca-sk/sk428")
    assert sk428.required is True
    assert sk428.title == "Form SK428: Saskatchewan Tax"
    assert tuple(sk428.exports) == (LINE_67, LINE_82)
    assert dict(sk428.supplies) == {"ca/provincial_tax.amount": LINE_82}
