"""The figure 5005-R line 89 will copy: the T2204 line 16 export at the Quebec rate.

5005-R line 89 (31200) "through employment (maximum $860.67)" is a copy of T2204 line 16 (ticket
R6 builds the copy). This test asserts that the form's export `ca/t2204_line_16`, with the
Quebec dataset swap, is the Quebec premium on the salary: 262.00, 860.67 and 860.67 at 20,000,
70,000 and 200,000.
"""

from __future__ import annotations

from decimal import Decimal

import pytest

from tax_engine.application.services.tax_computation import TaxComputationService
from tax_engine.jurisdictions.ca.catalog.refund import T2204_LINE_16
from tests.jurisdictions.ca_qc.test_take_home_t2204_line_4 import t2204

D = Decimal


@pytest.mark.parametrize(
    ("salary", "line_89"),
    [("20000", "262.00"), ("70000", "860.67"), ("200000", "860.67")],
)
def test_the_figure_line_89_copies(
    take_home_service: TaxComputationService, salary: str, line_89: str
) -> None:
    assert t2204(take_home_service, salary).get(T2204_LINE_16).value == D(line_89)
