"""The 2025 investment tax credit recapture rates, checked against CRA's Form T2038(IND).

2025 Form T2038(IND), Investment Tax Credit (Individuals), Part C - Recapture: "Amount of
expenditure on which ITC earned at 15% (after 2013) is recaptured. Do not enter more than the
amount of the original expenditure 67193 × 0.15 = 1" and "Amount of expenditure on which ITC earned
at 20% (before 2014) is recaptured. Do not enter more than the amount of the original expenditure
67195 × 0.20 = 2"; "Total recapture of investment tax credit on SR&ED expenditures (add amounts 1
and 2) Enter this amount on the Recapture of investment tax credit line of your income tax and
benefit return" (T1 line 131 for all provinces and territories, except Quebec). Each percentage is
a rate (the `rate` kind), rounded half-up to the cent, as every dollars-and-cents box on the forms
is. The form is a PDF with no published .txt, so the datasets cite the PDF.

The datasets are tested with the capabilities that read them, on made-up kinds; the lines together,
from the expenditures of lines 67193 and 67195 to line 42000, are in the `end_to_end` tests.
"""

from __future__ import annotations

from decimal import Decimal

import pytest

import tax_calculator.registrations
from tax_calculator.adapters.outbound.yaml_parameters import YamlParameterSource
from tax_calculator.domain.artifact import Artifact, ArtifactKind
from tax_calculator.domain.capabilities.apply_rate import ApplyRate
from tax_calculator.domain.capabilities.sum import Sum
from tax_calculator.domain.parameters.rate import RATE, Rate
from tax_calculator.domain.parameters.rounding import RoundingMode, RoundTo

D = Decimal
SOURCE = YamlParameterSource(tax_calculator.registrations.JURISDICTIONS.roots())
AFTER_2013 = "ca/itc_recapture_rate_after_2013"
BEFORE_2014 = "ca/itc_recapture_rate_before_2014"
T2038_PDF = "https://www.canada.ca/content/dam/cra-arc/formspubs/pbg/t2038-ind/t2038-ind-25e.pdf"
CENT = RoundTo(D("0.01"), RoundingMode.HALF_UP)

# Made up for this test and not registered: the two expenditures (lines 67193 and 67195), the two
# recaptures (amounts 1 and 2) and their total (amount 3).
EXPENDITURE_AT_15 = ArtifactKind("ex/expenditure_at_15", Decimal)
EXPENDITURE_AT_20 = ArtifactKind("ex/expenditure_at_20", Decimal)
RECAPTURE_AT_15 = ArtifactKind("ex/recapture_at_15", Decimal)
RECAPTURE_AT_20 = ArtifactKind("ex/recapture_at_20", Decimal)
RECAPTURE = ArtifactKind("ex/recapture", Decimal)


def test_2025_rate_after_2013_is_15_percent() -> None:
    data = SOURCE.get(AFTER_2013, 2025, RATE)

    assert data.values == Rate(D("0.15"))
    assert data.rounding == CENT


def test_2025_rate_before_2014_is_20_percent() -> None:
    data = SOURCE.get(BEFORE_2014, 2025, RATE)

    assert data.values == Rate(D("0.20"))
    assert data.rounding == CENT


def test_2025_datasets_cite_only_the_t2038_ind_pdf() -> None:
    assert SOURCE.get(AFTER_2013, 2025, RATE).sources == (T2038_PDF,)
    assert SOURCE.get(BEFORE_2014, 2025, RATE).sources == (T2038_PDF,)


@pytest.mark.parametrize(
    ("expenditure", "recapture"),
    [
        ("2000", "300.00"),
        ("0", "0.00"),
        # 0.03 x 15% = 0.0045, rounded half-up to 0.00; 0.10 x 15% = 0.015, a tie, up to 0.02.
        ("0.03", "0.00"),
        ("0.10", "0.02"),
    ],
)
def test_amount_1_is_15_percent_of_the_expenditure_on_line_67193(
    expenditure: str, recapture: str
) -> None:
    capability = ApplyRate(SOURCE.get(AFTER_2013, 2025, RATE), EXPENDITURE_AT_15, RECAPTURE_AT_15)

    result = capability.compute((Artifact(EXPENDITURE_AT_15, D(expenditure)),))

    assert result.outputs == (Artifact(RECAPTURE_AT_15, D(recapture)),)


@pytest.mark.parametrize(
    ("expenditure", "recapture"),
    [
        ("500", "100.00"),
        ("0", "0.00"),
        # 0.02 x 20% = 0.004, rounded half-up to 0.00; 0.03 x 20% = 0.006, up to 0.01.
        ("0.02", "0.00"),
        ("0.03", "0.01"),
    ],
)
def test_amount_2_is_20_percent_of_the_expenditure_on_line_67195(
    expenditure: str, recapture: str
) -> None:
    capability = ApplyRate(SOURCE.get(BEFORE_2014, 2025, RATE), EXPENDITURE_AT_20, RECAPTURE_AT_20)

    result = capability.compute((Artifact(EXPENDITURE_AT_20, D(expenditure)),))

    assert result.outputs == (Artifact(RECAPTURE_AT_20, D(recapture)),)


def test_amount_3_adds_amounts_1_and_2() -> None:
    at_15 = ApplyRate(SOURCE.get(AFTER_2013, 2025, RATE), EXPENDITURE_AT_15, RECAPTURE_AT_15)
    at_20 = ApplyRate(SOURCE.get(BEFORE_2014, 2025, RATE), EXPENDITURE_AT_20, RECAPTURE_AT_20)
    total = Sum((RECAPTURE_AT_15, RECAPTURE_AT_20), RECAPTURE)

    first = at_15.compute((Artifact(EXPENDITURE_AT_15, D("2000")),))
    second = at_20.compute((Artifact(EXPENDITURE_AT_20, D("500")),))
    result = total.compute((*first.outputs, *second.outputs))

    # 2,000 x 0.15 = 300.00 and 500 x 0.20 = 100.00, line 131 = 400.00.
    assert result.outputs == (Artifact(RECAPTURE, D("400.00")),)
