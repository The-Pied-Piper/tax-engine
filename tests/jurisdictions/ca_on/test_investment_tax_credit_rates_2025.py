"""The 2025 investment tax credit rates of Form T2038(IND) Parts A, B and E, against CRA's form.

2025 Form T2038(IND), Investment Tax Credit (Individuals), Part A, "Scientific research and
experimental development (SR&ED)": line 67120 "× 0.15 =" amount 1, line 67130 "× 0.15 =" amount 2,
and "Qualified property": line 67140 "× 0.10 =" amount 4. Part B, "Mineral exploration tax credit
(METC)": line 67170 "× 0.15 =" amount B; "Critical mineral exploration tax credit (CMETC)": line
67175 "× 0.30 =" amount C; "Apprenticeship job creation tax credit (AJCTC)": line 67180 "× 0.10 ="
amount D; "Repayment of assistance for SR&ED": line 67184 "× 0.20 =" amount 1 and line 67185
"× 0.15 =" amount 2. Part E, "Calculating an ITC refund": "The refundable rate" amount 18, printed
as "0.40", the rate at which amount 17 is refunded (amount O, line 45400). Each percentage is a
rate (the `rate` kind), rounded half-up to the cent, as every dollars-and-cents box on the forms
is. Confirmed from the PDF (docs/cra-forms-2025/t2038-ind-25e.pdf; no .txt published), so the
datasets cite the PDF.

The datasets are tested as rates on their own; the lines together, from the caller's figures to
amounts A and F, are in the `end_to_end` tests.
"""

from __future__ import annotations

from decimal import Decimal

import pytest

import tax_engine.registrations
from tax_engine.adapters.outbound.yaml_parameters import YamlParameterSource
from tax_engine.domain.parameters.rate import RATE, Rate
from tax_engine.domain.parameters.rounding import RoundingMode, RoundTo

D = Decimal
SOURCE = YamlParameterSource(tax_engine.registrations.JURISDICTIONS.roots())
T2038_PDF = "https://www.canada.ca/content/dam/cra-arc/formspubs/pbg/t2038-ind/t2038-ind-25e.pdf"
CENT = RoundTo(D("0.01"), RoundingMode.HALF_UP)

# (dataset, the rate the form prints)
RATES: tuple[tuple[str, str], ...] = (
    ("ca/itc_part_a_line_1_rate", "0.15"),
    ("ca/itc_part_a_line_2_rate", "0.15"),
    ("ca/itc_part_a_line_4_rate", "0.10"),
    ("ca/itc_part_b_amount_b_rate", "0.15"),
    ("ca/itc_part_b_amount_c_rate", "0.30"),
    ("ca/itc_part_b_amount_d_rate", "0.10"),
    ("ca/itc_part_b_repayment_line_1_rate", "0.20"),
    ("ca/itc_part_b_repayment_line_2_rate", "0.15"),
    ("ca/itc_part_e_refundable_rate", "0.40"),
)


@pytest.mark.parametrize(("family", "rate"), RATES, ids=[family for family, _ in RATES])
def test_2025_rate_is_the_percentage_the_form_prints(family: str, rate: str) -> None:
    data = SOURCE.get(family, 2025, RATE)

    assert data.values == Rate(D(rate))


@pytest.mark.parametrize(("family", "rate"), RATES, ids=[family for family, _ in RATES])
def test_2025_rate_rounds_half_up_to_the_cent(family: str, rate: str) -> None:
    # The form states no rounding rule; each credit is a dollars-and-cents box, so the product
    # rounds half-up to the cent, the owner's decision.
    data = SOURCE.get(family, 2025, RATE)

    assert data.rounding == CENT


@pytest.mark.parametrize(("family", "rate"), RATES, ids=[family for family, _ in RATES])
def test_2025_rate_cites_the_t2038_ind_form(family: str, rate: str) -> None:
    data = SOURCE.get(family, 2025, RATE)

    assert T2038_PDF in data.sources
