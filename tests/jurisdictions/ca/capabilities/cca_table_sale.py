"""Shared test data for the half-year rule on sale, T776 and T2125 Area A column 19.

The rows and helpers are those of `cca_table`. Its Class 10.1 does not have the rule, so a
Class 10.1 row there is worked as before; the class-rate dataset here lists Class 10.1 with the
half-year rule on sale (`HalfYearRuleOnSale.APPLIES`), as the 2025 dataset does, beside Class 1 and
Class 8, which do not have it. Guides T4036 and T4002, "Column 19 - Base amount for CCA":
"For a Class 10.1 vehicle you disposed of in your 2025 fiscal period, you may be able to claim 50%
of the CCA that would be allowed if you still owned the vehicle at the end of your 2025 fiscal
period. This is known as the half-year rule on sale. You can use the half-year rule on sale if, at
the end of your 2024 fiscal period, you owned the Class 10.1 vehicle you disposed of in 2025. If
this applies to you, enter 50% of the amount from column 2 (for Class 10.1 vehicles) in column
19."
"""

from __future__ import annotations

from tax_calculator.domain.parameters.class_rates import ClassRate, ClassRates, HalfYearRuleOnSale
from tax_calculator.domain.parameters.datasets import ParameterDataset
from tax_calculator.domain.parameters.rate import Rate
from tests.jurisdictions.ca.capabilities.cca_table import (
    APPLIES,
    CLASS_1,
    CLASS_8,
    EXCLUDED,
    D,
    F,
    class_rates,
)

ON_SALE = HalfYearRuleOnSale.APPLIES
NOT_ON_SALE = HalfYearRuleOnSale.DOES_NOT_APPLY

CLASS_10_1_ON_SALE = ClassRate(
    D("10.1"),
    Rate(D("0.30")),
    APPLIES,
    EXCLUDED,
    F(0, 1),
    F(1, 2),
    ON_SALE,
)


def sale_class_rates() -> ParameterDataset[ClassRates]:
    """Classes 1, 8 and 10.1, the last with the half-year rule on sale, to the cent."""
    return class_rates(classes=(CLASS_1, CLASS_8, CLASS_10_1_ON_SALE))
