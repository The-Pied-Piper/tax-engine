"""CA-ON 2025 end to end: return EI, the principal residence designation box of Schedule 3 Part 1.

Return EI is `returns/2025_return_ei.yaml`: three properties, each designated for every year it was
owned (the T4037 example), so Schedule 3 line 17900 is box 3. The other tests here vary the
properties, with the same starting values: no property is box 0, one property designated for all its
years is box 1 and one designated two years short is box 2. Each run gives the form's inputs to the
shared starting values.
"""

from __future__ import annotations

from tax_calculator.adapters.inbound.trace_english import EnglishTraceRenderer
from tax_calculator.domain.worksheet import Worksheet
from tax_calculator.jurisdictions.ca.catalog import PRINCIPAL_RESIDENCE_DESIGNATION_BOX
from tests.jurisdictions.ca.capabilities.principal_residence_figures import Figures
from tests.jurisdictions.ca_on.end_to_end.support import CA_ON, service, starting

# The T4037 example: each property owned and designated from 2000 to 2005 (6 years), from 2006 to
# 2010 (5 years) and from 2011 to 2025 (15 years), all after 1981, with no money: the box is worked
# from the years alone.
T4037_THREE_PROPERTIES: tuple[Figures, ...] = (
    (6, 0, 6, 0, "0.00", "0.00", "0.00", 0),
    (5, 0, 5, 0, "0.00", "0.00", "0.00", 0),
    (15, 0, 15, 0, "0.00", "0.00", "0.00", 0),
)


def schedule_3(*given: Figures) -> Worksheet:
    """The worksheet of Schedule 3 Part 1 of return EI, over the properties `given`; the return's
    other starting values are none."""
    result = service().compute(
        CA_ON,
        2025,
        *starting("0", (), "0", "0", "0", "0", "0", principal_residence_properties_rows=given),
    )
    (worksheet,) = result["ca/schedule_3"]
    return worksheet


def test_the_three_properties_of_the_t4037_example_are_box_3() -> None:
    worksheet = schedule_3(*T4037_THREE_PROPERTIES)
    rendered = EnglishTraceRenderer().render_all(worksheet.trace)

    assert worksheet.get(PRINCIPAL_RESIDENCE_DESIGNATION_BOX).value == 3
    assert (
        "principal_residence_designation_box: 3 = box 3, 3 properties (more than one property)"
        in (rendered)
    )


def test_no_property_leaves_line_17900_at_box_0() -> None:
    worksheet = schedule_3()

    assert worksheet.get(PRINCIPAL_RESIDENCE_DESIGNATION_BOX).value == 0


def test_one_property_designated_for_all_its_years_is_box_1() -> None:
    worksheet = schedule_3((6, 0, 6, 0, "0.00", "0.00", "0.00", 0))

    assert worksheet.get(PRINCIPAL_RESIDENCE_DESIGNATION_BOX).value == 1


def test_one_property_designated_two_years_short_is_box_2() -> None:
    worksheet = schedule_3((4, 0, 6, 0, "0.00", "0.00", "0.00", 0))

    assert worksheet.get(PRINCIPAL_RESIDENCE_DESIGNATION_BOX).value == 2
