"""MB479 (2025) line 15, the printed $62 of the disabled dependants row, as the Manitoba take-home
manifest wires it.

Form MB479 (CRA 5007-TC, 5007-tc-25e.txt), line 15: "multiplied by $62 =".

`core/credit_amount` takes the printed 62 from the `ca-
mb/disabled_dependants_credit_amount_line_15` dataset; it is not a line of the form, so it has
no reference. The real part is loaded beside a header made up here and the amount is read back;
the last test pins the part as printed.
"""

from __future__ import annotations

from pathlib import Path

import yaml

from tests.jurisdictions.ca_mb.mb428_medical_support import MB_PARTS, compute_line

FILE = "mb479_line_15_amount.yaml"
LINE = "ca-mb/disabled_dependants_credit_amount_line_15"


def test_line_15_amount_is_the_printed_figure(tmp_path: Path) -> None:
    value = compute_line(tmp_path, FILE, {}, LINE, form_name="ca-mb/mb479")

    assert str(value) == "62.00"


def test_the_part_is_as_printed() -> None:
    part = yaml.safe_load((MB_PARTS / FILE).read_text("utf-8"))

    assert list(part) == ["form", "capabilities"]
    assert part["form"] == {"name": "ca-mb/mb479"}
    assert part["capabilities"] == [
        {
            "name": "core/credit_amount",
            "title": "Amount for each disabled dependant",
            "unit": "ca/cad",
            "params": {"amount": LINE},
            "produces": {"output": LINE},
        }
    ]
