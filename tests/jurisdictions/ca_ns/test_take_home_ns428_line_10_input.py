"""NS428 (2025) line 10's input, as the Nova Scotia take-home manifest part declares it: whether the
filer was born in 1960 or earlier, the existing federal count `ca/born_in_1960_or_earlier` (a shared
fact, so no kind is declared here). A request that leaves it out is read as blank; the step that
reads it reads that blank as 0.
"""

from __future__ import annotations

from tests.jurisdictions.ca_ns import ns428_tax_support as s


def test_the_part_declares_only_the_born_in_1960_or_earlier_input() -> None:
    part = s.part("ns428_line_10_input.yaml")

    assert list(part) == ["form", "inputs"]
    assert part["form"] == {"name": "ca-ns/ns428"}
    assert part["inputs"] == [
        {
            "name": "ca/born_in_1960_or_earlier",
            "title": "Born in 1960 or earlier",
            "reference": "10",
            "required": False,
            "default": None,
            "basis": "Line 10 and line 98: if you were born in 1960 or earlier",
        }
    ]
