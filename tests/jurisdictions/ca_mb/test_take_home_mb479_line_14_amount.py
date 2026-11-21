"""MB479 (2025) line 14, the printed $113 of the disability row, as the Manitoba take-home manifest
wires it.

Form MB479 (CRA 5007-TC, 5007-tc-25e.txt), line 14: "multiplied by $113 =".

`core/credit_amount` takes the printed 113 from the `ca-mb/disability_credit_amount_line_14`
dataset; it is not a line of the form, so it has no reference. The real part is loaded beside a
header made up here and the amount is read back; the last test pins the part as printed.
"""

from __future__ import annotations

from pathlib import Path

import yaml

from tests.jurisdictions.ca_mb.mb428_medical_support import MB_PARTS, compute_line

FILE = "mb479_line_14_amount.yaml"
LINE = "ca-mb/disability_credit_amount_line_14"
COUNT = "ca-mb/mb479_disability_claims_number_line_14"


def test_line_14_amount_is_the_printed_figure(tmp_path: Path) -> None:
    value = compute_line(tmp_path, FILE, {COUNT: "1"}, LINE, form_name="ca-mb/mb479")

    assert str(value) == "113.00"


def test_the_part_is_as_printed() -> None:
    part = yaml.safe_load((MB_PARTS / FILE).read_text("utf-8"))

    assert list(part) == ["form", "capabilities"]
    assert part["form"] == {"name": "ca-mb/mb479"}
    assert part["capabilities"] == [
        {
            "name": "core/credit_amount",
            "unit": "ca/cad",
            "params": {"amount": LINE},
            "produces": {"output": LINE},
        }
    ]
