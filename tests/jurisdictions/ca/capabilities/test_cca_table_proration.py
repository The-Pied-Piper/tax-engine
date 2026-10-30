"""Unit tests for the proration of the CCA of a short fiscal period in the CCA table (`CcaTable`).

Guide T4002 2025, "You were asking?": "Q. How do I calculate my CCA claim if I start a business and
my first fiscal period is from June 1, 2025, to December 31, 2025? A. Since your fiscal period is
less than 365 days, you have to prorate your CCA claim. Calculate your CCA using the rules
discussed in this chapter. However, base your CCA claim on the number of days in your fiscal
period compared to 365 days. In this case, your fiscal period is 214 days. Suppose you calculate
your CCA to be $3,500. The amount of CCA you can claim is $2,052 ($3,500 × 214 ÷ 365)."

A table is prorated when it consumes the int kind of its `fiscal_period_days` slot (the number of
days of the fiscal period); a table without the slot is not (see the tests of `CcaClaim`,
`ClosingUcc` and the two after column 22). The slot is declared by four capabilities of their own,
one for each of those, as `CcaClaimAfterColumn22` declares `non_compliant`: a slot a capability
declares must be given, so the capabilities that have it are other ones:
`ca/cca_claim_prorated`, `ca/closing_ucc_prorated`, `ca/cca_claim_after_column_22_prorated` and
`ca/closing_ucc_after_column_22_prorated`. Each is its unprorated counterpart (see its tests) with
the maximum prorated; `RecapturedCca` and `TerminalLoss` do not depend on the maximum and have no
prorated counterpart.

The prorated maximum is column 19 multiplied by column 20 times the days over `full_year_days` of
the class-rates dataset (365 in 2025), as one exact fraction rounded once with the dataset's rule,
not the rounded maximum prorated. Column 9 (immediate expensing) is not prorated. The claim limit
(column 21) is the prorated maximum plus column 9 (less column 22 after column 22). A sale row's
prorated maximum is still at most its column 7. Days below 1 are refused
(`InputBelowBoundError`) and days above `full_year_days` are refused (`InputAboveBoundError`),
each naming the kind and the value.

Worked rows, by hand:
G, the guide's: Class 8 (20%), column 2 17,500.00 and nothing else: column 7 17,500.00, column 13
17,500.00, column 18 0, column 19 17,500.00, maximum 20% of 17,500.00 = 3,500.00 (the guide's
$3,500). 214 days: 3,500.00 x 214 / 365 = 749,000 / 365 = 2,052.0547..., rounded half-up to
2,052.05 (the guide prints $2,052); column 24 with that claim 17,500.00 - 2,052.05 = 15,447.95.
365 days: 3,500.00. 1 day: 3,500 / 365 = 9.589..., 9.59. 214 days with a column 22 of 500.00:
2,052.05 - 500.00 = 1,552.05.
O, one rounding: Class 10 (30%), column 2 10,000.01: column 19 10,000.01, 30% of it 3,000.003. At
214 days the exact 3,000.003 x 214 / 365 = 1,758.9058..., so 1,758.91; rounding the maximum first
(3,000.00) gives 1,758.90.
A, a DIEP: Class 8, column 2 1,000, column 3 5,000, column 4 4,000, column 9 3,000 (see
`test_cca_table_diep`): maximum 400.00; at 214 days 400.00 x 214 / 365 = 234.5205..., 234.52;
column 21 = 234.52 + 3,000 = 3,234.52.
S, a sale: Class 10.1 (30%, half-year rule on sale), column 2 10,000.00, proceeds 9,990.00, no
property left: column 7 10.00, column 19 5,000.00, maximum 1,500.00; at 214 days 1,500.00 x 214 /
365 = 879.45 (above column 7, so 10.00 is the maximum); at 1 day 1,500.00 / 365 = 4.1095..., 4.11
(below column 7, so 4.11).
"""

from __future__ import annotations

from collections.abc import Mapping
from decimal import Decimal
from typing import Any

import pytest

import tax_engine.jurisdictions.ca.capabilities as ca_capabilities
from tax_engine.domain.artifact import Artifact, ArtifactKind
from tax_engine.domain.capability import CapabilityRegistry, CapabilityResult
from tax_engine.domain.errors import (
    InputAboveBoundError,
    InputBelowBoundError,
    InvalidCapabilityError,
)
from tax_engine.domain.jurisdiction_code import JurisdictionCode
from tax_engine.domain.parameters.class_rates import ClassRates
from tax_engine.domain.parameters.datasets import ParameterDataset
from tax_engine.domain.record_list import RecordList
from tax_engine.jurisdictions.ca.capabilities.cca_claim import CcaClaim
from tax_engine.jurisdictions.ca.capabilities.cca_claim_after_column_22 import (
    CcaClaimAfterColumn22,
)
from tax_engine.jurisdictions.ca.capabilities.cca_claim_after_column_22_prorated import (
    CcaClaimAfterColumn22Prorated,
)
from tax_engine.jurisdictions.ca.capabilities.cca_claim_prorated import CcaClaimProrated
from tax_engine.jurisdictions.ca.capabilities.closing_ucc import ClosingUcc
from tax_engine.jurisdictions.ca.capabilities.closing_ucc_after_column_22 import (
    ClosingUccAfterColumn22,
)
from tax_engine.jurisdictions.ca.capabilities.closing_ucc_after_column_22_prorated import (
    ClosingUccAfterColumn22Prorated,
)
from tax_engine.jurisdictions.ca.capabilities.closing_ucc_prorated import ClosingUccProrated
from tax_engine.jurisdictions.ca.catalog import CCA_CLAIMED, CCA_CLASS_NUMBER, CCA_UCC_AT_END
from tax_engine.jurisdictions.ca.trace import CcaClaimLine, ClosingUccLine
from tests.jurisdictions.ca.capabilities.cca_table import (
    CCA_CLAIM,
    CLASSES,
    CLOSING_UCC,
    NO_COLUMN_22,
    NON_COMPLIANT,
    class_rates,
    classes,
    non_compliant_cca,
    row,
    service,
)
from tests.jurisdictions.ca.capabilities.cca_table_diep import (
    DIEP_CLASSES,
    diep_classes,
    diep_row,
)
from tests.jurisdictions.ca.capabilities.cca_table_sale import sale_class_rates

D = Decimal

FISCAL_PERIOD_DAYS = ArtifactKind("ex/fiscal_period_days", int)

# Row G of the module docstring: the guide's 3,500.00 maximum. Claims are set with `claiming`.
GUIDE = row("8", "17500")
# Row O: 30% of column 19 is 3,000.003.
ONE_ROUNDING = row("10", "10000.01")
# Row A, a DIEP; its claim is column 23, which includes column 9.
DIEP = diep_row("8", "1000", "5000", diep_additions="4000", immediate_expensing="3000")
# Row S, a sale.
SALE = row("10.1", "10000.00", proceeds="9990.00", no_property_left=1)

Row = dict[Any, Decimal | int]


def claiming(base: Row, claimed: str) -> Row:
    return {**base, CCA_CLAIMED: D(claimed)}


def days(count: int) -> Artifact[Any]:
    return Artifact(FISCAL_PERIOD_DAYS, count)


def compute(
    capability_class: type,
    count: int,
    rows: tuple[Row, ...],
    column_22: Artifact[Any] | None = None,
    dataset: ParameterDataset[ClassRates] | None = None,
    diep: bool = False,
) -> CapabilityResult:
    """The `capability_class` over `rows` for a fiscal period of `count` days. A class after column
    22 takes `column_22` (none by default)."""
    dataset = dataset or class_rates()
    kind = DIEP_CLASSES if diep else CLASSES
    given = diep_classes(*rows) if diep else classes(*rows)
    if capability_class in (CcaClaimProrated, ClosingUccProrated):
        built = capability_class(
            dataset, kind, fiscal_period_days=FISCAL_PERIOD_DAYS, output=_OUTPUTS[capability_class]
        )
        result: CapabilityResult = built.compute((given, days(count)))
        return result
    built = capability_class(
        dataset,
        kind,
        non_compliant=NON_COMPLIANT,
        fiscal_period_days=FISCAL_PERIOD_DAYS,
        output=_OUTPUTS[capability_class],
    )
    column_22_given = column_22 if column_22 is not None else NO_COLUMN_22
    result = built.compute((given, days(count), column_22_given))
    return result


_OUTPUTS: Mapping[type, ArtifactKind[Any]] = {
    CcaClaimProrated: CCA_CLAIM,
    CcaClaimAfterColumn22Prorated: CCA_CLAIM,
    ClosingUccProrated: CLOSING_UCC,
    ClosingUccAfterColumn22Prorated: CLOSING_UCC,
}
CLAIMS = [CcaClaimProrated, CcaClaimAfterColumn22Prorated]
CLOSINGS = [ClosingUccProrated, ClosingUccAfterColumn22Prorated]
ALL = [*CLAIMS, *CLOSINGS]


def claim_total(
    count: int,
    *rows: Row,
    column_22: Artifact[Any] | None = None,
    dataset: ParameterDataset[ClassRates] | None = None,
    diep: bool = False,
) -> Decimal:
    capability_class = CcaClaimAfterColumn22Prorated if column_22 is not None else CcaClaimProrated
    (output,) = compute(capability_class, count, rows, column_22, dataset, diep).outputs
    assert isinstance(output.value, Decimal)
    return output.value


def closing(
    count: int,
    *rows: Row,
    column_22: Artifact[Any] | None = None,
    dataset: ParameterDataset[ClassRates] | None = None,
) -> list[tuple[Decimal | int, Decimal | int]]:
    capability_class = (
        ClosingUccAfterColumn22Prorated if column_22 is not None else ClosingUccProrated
    )
    (output,) = compute(capability_class, count, rows, column_22, dataset).outputs
    assert isinstance(output.value, RecordList)
    return [(r[CCA_CLASS_NUMBER], r[CCA_UCC_AT_END]) for r in output.value.records]


# --- the capabilities ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    ("capability_class", "identifier", "module"),
    [
        (CcaClaimProrated, "ca/cca_claim_prorated", "cca_claim_prorated"),
        (ClosingUccProrated, "ca/closing_ucc_prorated", "closing_ucc_prorated"),
        (
            CcaClaimAfterColumn22Prorated,
            "ca/cca_claim_after_column_22_prorated",
            "cca_claim_after_column_22_prorated",
        ),
        (
            ClosingUccAfterColumn22Prorated,
            "ca/closing_ucc_after_column_22_prorated",
            "closing_ucc_after_column_22_prorated",
        ),
    ],
)
def test_is_registered_and_exported(capability_class: type, identifier: str, module: str) -> None:
    assert CapabilityRegistry.shared().get(identifier) is capability_class
    assert module in ca_capabilities.__all__
    assert getattr(ca_capabilities, module) is not None


@pytest.mark.parametrize(
    ("capability_class", "parent"),
    [
        (CcaClaimProrated, CcaClaim),
        (ClosingUccProrated, ClosingUcc),
        (CcaClaimAfterColumn22Prorated, CcaClaimAfterColumn22),
        (ClosingUccAfterColumn22Prorated, ClosingUccAfterColumn22),
    ],
)
def test_is_its_unprorated_counterpart(capability_class: type, parent: type) -> None:
    assert issubclass(capability_class, parent)


def test_declares_the_fiscal_period_days_slot_as_an_int() -> None:
    assert CcaClaimProrated.CONSUMES == {"classes": RecordList, "fiscal_period_days": int}
    assert ClosingUccProrated.CONSUMES == {"classes": RecordList, "fiscal_period_days": int}
    assert CcaClaimAfterColumn22Prorated.CONSUMES == {
        "classes": RecordList,
        "non_compliant": RecordList,
        "fiscal_period_days": int,
    }
    assert ClosingUccAfterColumn22Prorated.CONSUMES == {
        "classes": RecordList,
        "non_compliant": RecordList,
        "fiscal_period_days": int,
    }


def test_the_unprorated_capabilities_keep_their_slots() -> None:
    assert CcaClaim.CONSUMES == {"classes": RecordList}
    assert ClosingUcc.CONSUMES == {"classes": RecordList}
    assert CcaClaimAfterColumn22.CONSUMES == {"classes": RecordList, "non_compliant": RecordList}
    assert ClosingUccAfterColumn22.CONSUMES == {"classes": RecordList, "non_compliant": RecordList}


def test_consumes_the_fiscal_period_days_kind() -> None:
    built = CcaClaimProrated(
        class_rates(), CLASSES, fiscal_period_days=FISCAL_PERIOD_DAYS, output=CCA_CLAIM
    )

    assert built.consumes == frozenset({CLASSES, FISCAL_PERIOD_DAYS})
    assert built.produces == frozenset({CCA_CLAIM})


def test_rejects_a_money_kind_for_the_fiscal_period_days() -> None:
    with pytest.raises(InvalidCapabilityError, match="CcaClaimProrated.*'fiscal_period_days'"):
        CcaClaimProrated(
            class_rates(),
            CLASSES,
            fiscal_period_days=CCA_CLAIM,  # type: ignore[arg-type]
            output=CCA_CLAIM,
        )


# --- the claim: the guide's example -------------------------------------------------------------


@pytest.mark.parametrize("capability_class", CLAIMS)
def test_a_first_fiscal_period_of_214_days_prorates_the_maximum(capability_class: type) -> None:
    # Row G: 3,500.00 x 214 / 365 = 2,052.05 (the guide prints $2,052).
    result = compute(capability_class, 214, (claiming(GUIDE, "2052.05"),))

    (output,) = result.outputs
    assert output.value == D("2052.05")


@pytest.mark.parametrize("capability_class", CLAIMS)
def test_a_claim_above_the_prorated_maximum_is_refused(capability_class: type) -> None:
    with pytest.raises(InputAboveBoundError, match=r"^item 1: ca/cca_claimed 2052.06 is above the"):
        compute(capability_class, 214, (claiming(GUIDE, "2052.06"),))


@pytest.mark.parametrize("capability_class", CLAIMS)
def test_the_refusal_names_the_prorated_maximum(capability_class: type) -> None:
    with pytest.raises(InputAboveBoundError, match=r"above the maximum 2052.05"):
        compute(capability_class, 214, (claiming(GUIDE, "2052.06"),))


def test_a_claim_below_the_prorated_maximum_is_allowed() -> None:
    assert claim_total(214, claiming(GUIDE, "0")) == D("0")
    assert claim_total(214, claiming(GUIDE, "2000")) == D("2000")


def test_a_full_year_gives_the_unprorated_maximum() -> None:
    assert claim_total(365, claiming(GUIDE, "3500.00")) == D("3500.00")
    with pytest.raises(InputAboveBoundError, match=r"above the maximum 3500.00"):
        claim_total(365, claiming(GUIDE, "3500.01"))


def test_365_days_gives_the_result_of_the_unprorated_capability() -> None:
    given = claiming(GUIDE, "3500.00")
    plain = CcaClaim(class_rates(), CLASSES, CCA_CLAIM).compute((classes(given),))
    prorated = compute(CcaClaimProrated, 365, (given,))

    assert prorated.outputs == plain.outputs


def test_366_days_is_a_full_year_not_prorated_to_366_over_365() -> None:
    # Guide T4002 prorates a period "less than 365 days": 1 Feb 2024 to 31 Jan 2025 is 366 days
    # and the maximum stays 3,500.00, not 3,500.00 x 366 / 365 = 3,509.59.
    assert claim_total(366, claiming(GUIDE, "3500.00")) == D("3500.00")
    with pytest.raises(InputAboveBoundError, match=r"above the maximum 3500.00"):
        claim_total(366, claiming(GUIDE, "3500.01"))


def test_one_day_gives_one_365th_of_the_maximum() -> None:
    # 3,500.00 / 365 = 9.589..., 9.59.
    assert claim_total(1, claiming(GUIDE, "9.59")) == D("9.59")
    with pytest.raises(InputAboveBoundError, match=r"above the maximum 9.59"):
        claim_total(1, claiming(GUIDE, "9.60"))


def test_the_maximum_is_prorated_as_one_exact_fraction_rounded_once() -> None:
    # Row O: 3,000.003 x 214 / 365 = 1,758.9058 gives 1,758.91, not 1,758.90 from the rounded
    # 3,000.00.
    assert claim_total(214, claiming(ONE_ROUNDING, "1758.91")) == D("1758.91")
    with pytest.raises(InputAboveBoundError, match=r"above the maximum 1758.91"):
        claim_total(214, claiming(ONE_ROUNDING, "1758.92"))


def test_each_class_is_prorated_and_the_claims_are_totalled() -> None:
    # Class 8 (3,500.00 -> 2,052.05) and Class 10 (3,000.003 -> 1,758.91).
    rows = (claiming(GUIDE, "2052.05"), claiming(ONE_ROUNDING, "1758.91"))

    assert claim_total(214, *rows) == D("3810.96")


# --- the days of the fiscal period --------------------------------------------------------------


@pytest.mark.parametrize("capability_class", ALL)
@pytest.mark.parametrize("count", [0, -1, -365])
def test_days_below_1_are_refused(capability_class: type, count: int) -> None:
    with pytest.raises(
        InputBelowBoundError, match=rf"ex/fiscal_period_days {count} is below the minimum 1"
    ):
        compute(capability_class, count, (GUIDE,))


@pytest.mark.parametrize("capability_class", ALL)
@pytest.mark.parametrize("count", [367, 1000])
def test_days_above_366_are_refused(capability_class: type, count: int) -> None:
    with pytest.raises(
        InputAboveBoundError, match=rf"ex/fiscal_period_days {count} is above the maximum 366"
    ):
        compute(capability_class, count, (GUIDE,))


@pytest.mark.parametrize("capability_class", ALL)
@pytest.mark.parametrize("count", [1, 214, 365, 366])
def test_days_from_1_to_366_are_accepted(capability_class: type, count: int) -> None:
    compute(capability_class, count, (GUIDE,))


def test_the_days_in_a_full_year_are_the_datasets() -> None:
    # A dataset of 366 days: 3,500.00 x 214 / 366 = 2,046.448..., 2,046.45; 366 days is a full year.
    leap = class_rates(full_year_days=366)

    assert claim_total(214, claiming(GUIDE, "2046.45"), dataset=leap) == D("2046.45")
    with pytest.raises(InputAboveBoundError, match=r"above the maximum 2046.45"):
        claim_total(214, claiming(GUIDE, "2046.46"), dataset=leap)
    assert claim_total(366, claiming(GUIDE, "3500.00"), dataset=leap) == D("3500.00")
    with pytest.raises(InputAboveBoundError, match=r"is above the maximum 366"):
        compute(CcaClaimProrated, 367, (GUIDE,), dataset=leap)


# --- column 9 and column 22 ---------------------------------------------------------------------


def test_column_9_is_not_prorated() -> None:
    # Row A: maximum 400.00 x 214 / 365 = 234.52, plus column 9 3,000 = 3,234.52.
    assert claim_total(214, claiming(DIEP, "3234.52"), diep=True) == D("3234.52")
    with pytest.raises(InputAboveBoundError, match=r"above the maximum 3234.52"):
        claim_total(214, claiming(DIEP, "3234.53"), diep=True)


def test_the_claim_is_at_least_column_9_even_when_prorated() -> None:
    assert claim_total(214, claiming(DIEP, "3000"), diep=True) == D("3000")
    with pytest.raises(InputBelowBoundError):
        claim_total(214, claiming(DIEP, "2999.99"), diep=True)


def test_the_claim_after_column_22_is_the_prorated_maximum_less_column_22() -> None:
    # 2,052.05 - 500.00 = 1,552.05.
    column_22 = non_compliant_cca(("8", "500.00"))

    assert claim_total(214, claiming(GUIDE, "1552.05"), column_22=column_22) == D("1552.05")
    with pytest.raises(InputAboveBoundError, match=r"above the maximum 1552.05"):
        claim_total(214, claiming(GUIDE, "1552.06"), column_22=column_22)


def test_a_column_22_above_the_prorated_maximum_allows_no_claim() -> None:
    column_22 = non_compliant_cca(("8", "2100.00"))

    assert claim_total(214, claiming(GUIDE, "0"), column_22=column_22) == D("0")
    with pytest.raises(InputAboveBoundError):
        claim_total(214, claiming(GUIDE, "0.01"), column_22=column_22)


# --- the closing UCC ----------------------------------------------------------------------------


def test_the_closing_ucc_is_column_7_less_the_prorated_claim() -> None:
    # Row G: 17,500.00 - 2,052.05 = 15,447.95.
    assert closing(214, claiming(GUIDE, "2052.05")) == [(D("8"), D("15447.95"))]


def test_the_closing_ucc_refuses_a_claim_above_the_prorated_maximum() -> None:
    with pytest.raises(InputAboveBoundError, match=r"above the maximum 2052.05"):
        closing(214, claiming(GUIDE, "2052.06"))


def test_the_closing_ucc_after_column_22_uses_the_prorated_limit() -> None:
    column_22 = non_compliant_cca(("8", "500.00"))

    assert closing(214, claiming(GUIDE, "1552.05"), column_22=column_22) == [
        (D("8"), D("15947.95"))
    ]
    with pytest.raises(InputAboveBoundError, match=r"above the maximum 1552.05"):
        closing(214, claiming(GUIDE, "1552.06"), column_22=column_22)


def test_a_full_year_closes_as_the_unprorated_closing_ucc() -> None:
    given = claiming(GUIDE, "3500.00")
    plain = ClosingUcc(class_rates(), CLASSES, CLOSING_UCC).compute((classes(given),))

    assert compute(ClosingUccProrated, 365, (given,)).outputs == plain.outputs


# --- a sale row ---------------------------------------------------------------------------------


def sale_claim_total(count: int, claimed: str) -> Decimal:
    capability = CcaClaimProrated(
        sale_class_rates(), CLASSES, fiscal_period_days=FISCAL_PERIOD_DAYS, output=CCA_CLAIM
    )
    (output,) = capability.compute((classes(claiming(SALE, claimed)), days(count))).outputs
    assert isinstance(output.value, Decimal)
    return output.value


def test_a_sale_rows_prorated_maximum_is_not_limited_to_column_7() -> None:
    # 1,500.00 x 214 / 365 = 879.45 is above column 7 (10.00) and is the maximum.
    assert sale_claim_total(214, "879.45") == D("879.45")
    with pytest.raises(InputAboveBoundError, match=r"above the maximum 879.45"):
        sale_claim_total(214, "879.46")


def test_a_sale_rows_prorated_maximum_below_column_7_is_the_maximum() -> None:
    # 1,500.00 / 365 = 4.11 is below column 7 (10.00).
    assert sale_claim_total(1, "4.11") == D("4.11")
    with pytest.raises(InputAboveBoundError, match=r"above the maximum 4.11"):
        sale_claim_total(1, "4.12")


# --- zero rows ----------------------------------------------------------------------------------


def test_a_row_with_no_maximum_is_still_no_claim() -> None:
    # Column 7 is negative: the maximum is 0 whatever the days.
    negative = row("8", "1000", proceeds="5000")

    assert claim_total(214, claiming(negative, "0")) == D("0")
    with pytest.raises(InputAboveBoundError):
        claim_total(214, claiming(negative, "0.01"))


# --- the trace ----------------------------------------------------------------------------------


def lines(result: CapabilityResult, line_class: type) -> list[Any]:
    return [line for line in result.trace if isinstance(line, line_class)]


@pytest.mark.parametrize("capability_class", CLAIMS)
def test_the_claim_line_holds_the_prorated_maximum_and_the_days(capability_class: type) -> None:
    result = compute(capability_class, 214, (claiming(GUIDE, "2052.05"),))

    (line,) = lines(result, CcaClaimLine)
    assert line.fiscal_period_days == 214
    assert line.column_19 == D("17500.00")
    assert line.maximum == D("2052.05")
    assert line.claim == D("2052.05")


@pytest.mark.parametrize("capability_class", CLAIMS)
def test_the_claim_line_of_a_full_year_holds_365_days(capability_class: type) -> None:
    result = compute(capability_class, 365, (claiming(GUIDE, "3500.00"),))

    (line,) = lines(result, CcaClaimLine)
    assert line.fiscal_period_days == 365
    assert line.maximum == D("3500.00")


@pytest.mark.parametrize("capability_class", CLOSINGS)
def test_the_closing_line_holds_the_days_and_the_prorated_claim(capability_class: type) -> None:
    result = compute(capability_class, 214, (claiming(GUIDE, "2052.05"),))

    (line,) = lines(result, ClosingUccLine)
    assert line.fiscal_period_days == 214
    assert line.claim == D("2052.05")
    assert line.result == D("15447.95")


def test_the_lines_of_an_unprorated_table_hold_365_days() -> None:
    given = (classes(claiming(GUIDE, "3500.00")),)

    claim_trace: tuple[Any, ...] = CcaClaim(class_rates(), CLASSES, CCA_CLAIM).compute(given).trace
    closing_trace: tuple[Any, ...] = (
        ClosingUcc(class_rates(), CLASSES, CLOSING_UCC).compute(given).trace
    )
    (claim_line, _total) = claim_trace
    (closing_line,) = closing_trace
    assert claim_line.fiscal_period_days == 365
    assert closing_line.fiscal_period_days == 365


def test_an_unprorated_table_is_unchanged_by_a_fiscal_period_it_does_not_consume() -> None:
    # The unprorated claim of row G is the full 3,500.00.
    with pytest.raises(InputAboveBoundError, match=r"above the maximum 3500.00"):
        CcaClaim(class_rates(), CLASSES, CCA_CLAIM).compute((classes(claiming(GUIDE, "3500.01")),))


# --- through TaxComputationService --------------------------------------------------------------


def test_a_computation_prorates_the_guides_example() -> None:
    worksheet = service(
        "ca/cca_claim_prorated", CCA_CLAIM, extra={"fiscal_period_days": FISCAL_PERIOD_DAYS}
    ).compute(JurisdictionCode("CA-ON"), 2025, classes(claiming(GUIDE, "2052.05")), days(214))[
        "ca-on/return"
    ][0]

    assert worksheet.get(CCA_CLAIM).value == D("2052.05")


def test_a_computation_refuses_the_claim_above_the_prorated_maximum() -> None:
    computing = service(
        "ca/cca_claim_prorated", CCA_CLAIM, extra={"fiscal_period_days": FISCAL_PERIOD_DAYS}
    )

    with pytest.raises(InputAboveBoundError, match=r"above the maximum 2052.05"):
        computing.compute(
            JurisdictionCode("CA-ON"), 2025, classes(claiming(GUIDE, "2052.06")), days(214)
        )
