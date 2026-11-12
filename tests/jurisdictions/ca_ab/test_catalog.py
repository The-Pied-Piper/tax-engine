"""The Alberta catalog: the AB428 line 75 kind.

Form text (Form AB428, CRA 5009-c-25e.txt): "Line 75: Line 73 minus line 74 (if negative, enter "0")
Enter this amount on line 42800 of your return. Alberta tax =".
"""

from __future__ import annotations

from tax_engine.domain.kinds import AmountKind
from tests.jurisdictions.ca_ab.support import alberta_kinds

LINE_75 = "ca-ab/ab428_alberta_tax_line_75"


def test_ab428_line_75_is_registered_in_the_alberta_package_list() -> None:
    assert LINE_75 in alberta_kinds().identifiers()


def test_ab428_line_75_is_a_non_negative_amount() -> None:
    kind = alberta_kinds().kind(LINE_75)

    assert isinstance(kind, AmountKind)
    assert kind.non_negative is True


def test_ab428_line_75_is_the_catalogs_object() -> None:
    from tax_engine.jurisdictions.ca_ab.catalog import AB428_ALBERTA_TAX_LINE_75

    assert alberta_kinds().kind(LINE_75) is AB428_ALBERTA_TAX_LINE_75
