"""The NB428 form declaration, loaded from the real part file beside a test header.

Form text (Form NB428, New Brunswick Tax, CRA 5004-C): line 97 "Enter this amount on line 42800 of
your return." The form is one form (lines 1 to 97) and exports line 97, the New Brunswick tax, and
supplies line 97 as `ca/provincial_tax.amount`, the name the federal T1 reads for line 42800. The
form also exports line 5, "Rate", line 83, "Line 81 minus line 82 (if negative, enter "0")", and
line 86, the low-income tax reduction, and the age amount worksheet's line 4 and the age amount
claimed (line 10 before the printed maximum check), the figures the return summary reads for the
marginal tax rate. Each export is declared as an input of the test header: this test loads only
the form declaration (`nb428.yaml`), not the line parts, which have their own tests.
"""

from __future__ import annotations

from pathlib import Path

import tax_engine.jurisdictions.ca_nb
from tax_engine.adapters.outbound.yaml_jurisdictions import YamlJurisdictionSource
from tests.jurisdictions.ca_nb.support import (
    new_brunswick_kinds,
    new_brunswick_packages,
    new_brunswick_units,
)

PART = Path(tax_engine.jurisdictions.ca_nb.__file__).parent / "manifests" / "2025" / "nb428.yaml"
LINE_5 = "ca-nb/nb428_bracket_rate_line_5"
LINE_83 = "ca-nb/nb428_line_83"
LINE_86 = "ca-nb/nb428_line_86"
LINE_97 = "ca-nb/nb428_new_brunswick_tax_line_97"
AGE_LINE_4 = "ca-nb/worksheet_nb428_age_amount_line_4"
AGE_CLAIMED = "ca-nb/nb428_age_amount_claimed_line_10"

HEADER = """\
jurisdiction: CA-NB
version: 1
valid_from_tax_year: 2025
inputs: []
outputs: []
capabilities: []
"""
# The inputs belong to the form that exports them, so they are declared in a part of that form.
OWNED_INPUTS = f"""\
form:
  name: ca-nb/nb428
inputs:
  - name: {LINE_5}
    required: true
  - name: {LINE_83}
    required: true
  - name: {LINE_86}
    required: true
  - name: {LINE_97}
    required: true
  - name: {AGE_LINE_4}
    required: true
  - name: {AGE_CLAIMED}
    required: true
"""


def test_the_form_is_declared_with_its_export_and_supply(tmp_path: Path) -> None:
    folder = tmp_path / "manifests" / "2025"
    folder.mkdir(parents=True)
    (folder / "00_header.yaml").write_text(HEADER, encoding="utf-8")
    (folder / "00_inputs.yaml").write_text(OWNED_INPUTS, encoding="utf-8")
    (folder / "01_nb428.yaml").write_text(PART.read_text(encoding="utf-8"), encoding="utf-8")
    source = YamlJurisdictionSource(
        new_brunswick_packages().roots(),
        new_brunswick_kinds(),
        new_brunswick_units(),
    )

    manifest = source.load(folder)

    (nb428,) = (form for form in manifest.forms if form.name == "ca-nb/nb428")
    assert nb428.required is True
    assert nb428.title == "Form NB428: New Brunswick Tax and Credits"
    assert tuple(nb428.exports) == (
        LINE_5,
        LINE_83,
        LINE_86,
        LINE_97,
        AGE_LINE_4,
        AGE_CLAIMED,
    )
    assert dict(nb428.supplies) == {"ca/provincial_tax.amount": LINE_97}
