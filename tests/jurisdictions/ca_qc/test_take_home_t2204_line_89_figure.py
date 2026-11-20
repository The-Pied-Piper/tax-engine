"""The figure 5005-R line 89 will copy: the T2204 line 16 export at the Quebec rate.

5005-R line 89 (31200) "through employment (maximum $860.67)" is a copy of T2204 line 16 (the
copy is built with the 5005-R lines 85 to 100). T2204 line 16 is the least of line 7, line 9 (line
4) and line 12 (the required premium), so with the salary alone it is the Quebec premium: line 4,
line 10 and line 16 are one figure, 262.00, 860.67 and 860.67 at 20,000, 70,000 and 200,000.
"""

from __future__ import annotations

from decimal import Decimal

import pytest

from tax_engine.application.services.tax_computation import TaxComputationService
from tax_engine.jurisdictions.ca.catalog.refund import (
    T2204_LINE_10,
    T2204_LINE_16,
    T2204_PREMIUMS_DEDUCTED,
)
from tests.jurisdictions.ca_qc.support import t2204_worksheet

D = Decimal


@pytest.mark.parametrize(
    ("salary", "line_89"),
    [("20000", "262.00"), ("70000", "860.67"), ("200000", "860.67")],
)
def test_the_figure_line_89_copies_is_line_16_and_the_quebec_premium(
    take_home_service: TaxComputationService, salary: str, line_89: str
) -> None:
    sheet = t2204_worksheet(take_home_service, salary)

    assert sheet.get(T2204_LINE_16).value == D(line_89)
    assert sheet.get(T2204_PREMIUMS_DEDUCTED).value == D(line_89)
    assert sheet.get(T2204_LINE_10).value == D(line_89)
