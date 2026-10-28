"""English text of PrincipalResidenceDesignationBox: Schedule 3 line 17900, the principal residence
designation box, one sentence for each box and for no property.

The sentence names the output (its label, `principal_residence_designation_box`), then the box, then
the figures it is worked from: the count of properties for box 3, and the years designated and owned
of the one property for boxes 1 and 2. No property is box 0, and no box is ticked.
"""

from __future__ import annotations

from typing import cast

import pytest

from tax_calculator.adapters.inbound.trace_english import EnglishTraceRenderer
from tax_calculator.domain.trace.base import TraceLine
from tax_calculator.jurisdictions.ca.catalog import PRINCIPAL_RESIDENCE_DESIGNATION_BOX
from tax_calculator.jurisdictions.ca.trace import PrincipalResidenceDesignationBox


def render(line: TraceLine) -> str:
    return EnglishTraceRenderer().render(line)


@pytest.mark.parametrize(
    ("line", "text"),
    [
        (
            PrincipalResidenceDesignationBox(
                output=PRINCIPAL_RESIDENCE_DESIGNATION_BOX,
                properties=0,
                designated=0,
                owned=0,
                box=0,
            ),
            "principal_residence_designation_box: 0 = no property, so no box is ticked",
        ),
        (
            PrincipalResidenceDesignationBox(
                output=PRINCIPAL_RESIDENCE_DESIGNATION_BOX,
                properties=1,
                designated=6,
                owned=6,
                box=1,
            ),
            "principal_residence_designation_box: 1 = box 1, one property designated for 6 of its "
            "6 years owned (all, or all but one)",
        ),
        (
            PrincipalResidenceDesignationBox(
                output=PRINCIPAL_RESIDENCE_DESIGNATION_BOX,
                properties=1,
                designated=4,
                owned=6,
                box=2,
            ),
            "principal_residence_designation_box: 2 = box 2, one property designated for 4 of its "
            "6 years owned (some but not all)",
        ),
        (
            PrincipalResidenceDesignationBox(
                output=PRINCIPAL_RESIDENCE_DESIGNATION_BOX,
                properties=3,
                designated=0,
                owned=0,
                box=3,
            ),
            "principal_residence_designation_box: 3 = box 3, 3 properties (more than one property)",
        ),
    ],
)
def test_renders_the_box_in_its_form_words(
    line: PrincipalResidenceDesignationBox, text: str
) -> None:
    assert render(cast(TraceLine, line)) == text
