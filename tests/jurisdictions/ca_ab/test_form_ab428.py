"""The AB428 form declaration, read from the real part file.

Form text (Form AB428, CRA 5009-c-25e.txt): "Line 75: Line 73 minus line 74 (if negative, enter "0")
Enter this amount on line 42800 of your return. Alberta tax =".
The form exports line 75 and supplies it as `ca/provincial_tax.amount`, the name the federal T1
reads for line 42800. Line 75 has no step yet, so it is declared as an input of the test header.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml

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


def _form() -> dict[str, Any]:
    document = yaml.safe_load(PART.read_text(encoding="utf-8"))
    assert isinstance(document, dict)
    form = document["form"]
    assert isinstance(form, dict)
    return form


def test_the_part_file_declares_the_form() -> None:
    form = _form()

    assert form["name"] == "ca-ab/ab428"
    assert form["title"] == "Form AB428: Alberta Tax and Credits"
    assert form["required"] is True


def test_the_form_exports_line_75_and_supplies_it_as_the_provincial_tax() -> None:
    form = _form()

    assert form["exports"] == [LINE_75]
    assert form["supplies"] == {"ca/provincial_tax.amount": LINE_75}


def test_the_part_declares_no_capabilities() -> None:
    document = yaml.safe_load(PART.read_text(encoding="utf-8"))

    assert document["capabilities"] == []
    assert _form().get("capabilities", []) == []


def test_the_engine_loads_the_part_beside_a_header(tmp_path: Path) -> None:
    folder = tmp_path / "manifests" / "2025"
    folder.mkdir(parents=True)
    (folder / "00_header.yaml").write_text(HEADER, encoding="utf-8")
    (folder / "01_ab428.yaml").write_text(PART.read_text(encoding="utf-8"), encoding="utf-8")
    source = YamlJurisdictionSource(alberta_packages().roots(), alberta_kinds(), alberta_units())

    manifest = source.load(folder)

    (ab428,) = (form for form in manifest.forms if form.name == "ca-ab/ab428")
    assert ab428.title == "Form AB428: Alberta Tax and Credits"
    assert tuple(ab428.exports) == (LINE_75,)
    assert dict(ab428.supplies) == {"ca/provincial_tax.amount": LINE_75}
