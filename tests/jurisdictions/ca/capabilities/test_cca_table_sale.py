"""Unit tests for the half-year rule on sale in the CCA table (`CcaTable`), Area A column 19.

Guides T4036 and T4002, "Column 19 - Base amount for CCA": "For a Class 10.1 vehicle you disposed
of in your 2025 fiscal period, you may be able to claim 50% of the CCA that would be allowed if you
still owned the vehicle at the end of your 2025 fiscal period. This is known as the half-year rule
on sale. You can use the half-year rule on sale if, at the end of your 2024 fiscal period, you
owned the Class 10.1 vehicle you disposed of in 2025. If this applies to you, enter 50% of the
amount from column 2 (for Class 10.1 vehicles) in column 19." T776 Area A: "Column 19: Base amount
for CCA (column 13 plus column 15 plus column 17 minus column 18)".

A row uses the rule when its class has the flag (`half_year_rule_on_sale` of the class rates), its
column 2 is above 0 and the caller says no property is left in the class. Then column 19 is one
half of column 2, the exact half rounded once with the dataset's rule, in place of column 13 plus
columns 15 and 17 minus column 18; the zero of "no property left" and of a column 7 at or below 0
does not apply, so the maximum is column 19 times the class's rate, not limited to column 7:
Regulation 1100(2.5)
(https://laws-lois.justice.gc.ca/eng/regulations/C.R.C.,_c._945/section-1100.html) determines
the deduction "as if the property had not been disposed of" with one-half of the days.
Column 24 is 0, as the rest of the UCC is not deductible later (Folio S3-F4-C1 paragraph 1.106).
Recapture and a terminal loss stay 0 for Class 10.1 (Note 3). A column 2 of 0, a class without the
flag and a class with property left are worked as before.

Worked row S, Class 10.1 (30%), column 2 20,000.00, proceeds (column 5) 12,000.00, no property
left: column 7 is 20,000.00 + 0 - 12,000.00 = 8,000.00; column 19 is one half of 20,000.00 =
10,000.00; maximum 10,000.00 x 30% = 3,000.00; with a claim of 3,000.00 column 24 is 8,000.00 -
3,000.00 = 5,000.00 in the table, but the row closes at 0.
Row R, column 2 20,001.01: column 7 8,001.01; column 19 is 20,001.01 / 2 = 10,000.505, rounded
half-up once to 10,000.51; maximum 10,000.51 x 30% = 3,000.153, rounded to 3,000.15.
Row A, row S with additions of 5,000 (column 3): column 7 13,000.00; column 19 still 10,000.00;
maximum 3,000.00; column 24 with the full claim 10,000.00.
"""

from __future__ import annotations

from decimal import Decimal
from typing import Any

import pytest

from tax_engine.domain.artifact import Artifact
from tax_engine.domain.errors import InputAboveBoundError
from tax_engine.domain.record_list import RecordList
from tax_engine.domain.trace import ItemsTotalLine
from tax_engine.jurisdictions.ca.capabilities.cca_claim import CcaClaim
from tax_engine.jurisdictions.ca.capabilities.cca_claim_after_column_22 import (
    CcaClaimAfterColumn22,
)
from tax_engine.jurisdictions.ca.capabilities.closing_ucc import ClosingUcc
from tax_engine.jurisdictions.ca.capabilities.recaptured_cca import RecapturedCca
from tax_engine.jurisdictions.ca.capabilities.terminal_loss import TerminalLoss
from tax_engine.jurisdictions.ca.catalog import CCA_CLASS_NUMBER, CCA_UCC_AT_END
from tax_engine.jurisdictions.ca.trace import (
    CcaClaimLine,
    CcaZeroReason,
    ClosingUccLine,
    TerminalLossLine,
)
from tests.jurisdictions.ca.capabilities.cca_table import (
    CCA_CLAIM,
    CENT,
    CLASS_1,
    CLASS_10_1,
    CLASSES,
    CLOSING_UCC,
    NON_COMPLIANT,
    RECAPTURED_CCA,
    TERMINAL_LOSS,
    class_rates,
    classes,
    non_compliant_cca,
    row,
)
from tests.jurisdictions.ca.capabilities.cca_table_sale import (
    CLASS_10_1_ON_SALE,
    NOT_ON_SALE,
    ON_SALE,
    sale_class_rates,
)

D = Decimal


def sold(claimed: str = "0", column_2: str = "20000.00", **kwargs: Any) -> dict[Any, Decimal | int]:
    """Class 10.1 with `column_2` at the start, proceeds of 12,000.00 and no property left."""
    kwargs.setdefault("proceeds", "12000.00")
    return row("10.1", column_2, claimed=claimed, no_property_left=1, **kwargs)


def claim_total(*rows: dict[Any, Decimal | int]) -> Decimal:
    result = CcaClaim(sale_class_rates(), CLASSES, CCA_CLAIM).compute((classes(*rows),))
    (output,) = result.outputs
    assert isinstance(output.value, Decimal)
    return output.value


def claim_trace(*rows: dict[Any, Decimal | int]) -> tuple[Any, ...]:
    return CcaClaim(sale_class_rates(), CLASSES, CCA_CLAIM).compute((classes(*rows),)).trace


def closing(*rows: dict[Any, Decimal | int]) -> list[tuple[Decimal | int, Decimal | int]]:
    result = ClosingUcc(sale_class_rates(), CLASSES, CLOSING_UCC).compute((classes(*rows),))
    (output,) = result.outputs
    assert isinstance(output.value, RecordList)
    return [(r[CCA_CLASS_NUMBER], r[CCA_UCC_AT_END]) for r in output.value.records]


def recapture(*rows: dict[Any, Decimal | int]) -> Artifact[Any]:
    capability = RecapturedCca(sale_class_rates(), CLASSES, RECAPTURED_CCA)
    (output,) = capability.compute((classes(*rows),)).outputs
    return output


def terminal_loss(*rows: dict[Any, Decimal | int]) -> Artifact[Any]:
    capability = TerminalLoss(sale_class_rates(), CLASSES, TERMINAL_LOSS)
    (output,) = capability.compute((classes(*rows),)).outputs
    return output


# --- the class-rate flag ------------------------------------------------------------------------


def test_a_class_has_the_half_year_rule_on_sale_unless_it_is_given_it() -> None:
    assert CLASS_10_1_ON_SALE.half_year_rule_on_sale is ON_SALE
    assert CLASS_10_1.half_year_rule_on_sale is NOT_ON_SALE
    assert CLASS_1.half_year_rule_on_sale is NOT_ON_SALE


# --- the claim ----------------------------------------------------------------------------------


def test_a_class_10_1_vehicle_sold_claims_up_to_30_percent_of_half_of_column_2() -> None:
    # Row S: maximum 3,000.00.
    assert claim_total(sold("3000.00")) == D("3000.00")


def test_a_claim_above_the_half_year_rule_on_sale_maximum_is_refused() -> None:
    with pytest.raises(InputAboveBoundError, match=r"^item 1: ca/cca_claimed 3000.01 is above"):
        claim_total(sold("3000.01"))


def test_the_refusal_names_the_maximum() -> None:
    with pytest.raises(InputAboveBoundError, match=r"above the maximum 3000.00"):
        claim_total(sold("3000.01"))


def test_a_claim_below_the_maximum_is_allowed() -> None:
    assert claim_total(sold("0")) == D("0")
    assert claim_total(sold("1234.56")) == D("1234.56")


def test_column_19_is_one_half_of_column_2_rounded_once() -> None:
    # Row R: 20,001.01 / 2 = 10,000.505 rounds to 10,000.51 and the maximum to 3,000.15.
    assert claim_total(sold("3000.15", column_2="20001.01")) == D("3000.15")
    with pytest.raises(InputAboveBoundError, match=r"above the maximum 3000.15"):
        claim_total(sold("3000.16", column_2="20001.01"))


def test_additions_in_the_year_do_not_change_column_19() -> None:
    # Row A: column 19 is one half of column 2, not column 13 plus columns 15 and 17 minus 18.
    added = sold("3000.00", additions="5000")
    assert claim_total(added) == D("3000.00")
    with pytest.raises(InputAboveBoundError):
        claim_total(sold("3000.01", additions="5000"))


def test_the_rule_needs_no_property_left() -> None:
    # Property left in the class: column 19 is column 13 plus columns 15 and 17 minus column 18 =
    # 20,000.00 + 0 + 0 - 0, the maximum 6,000.00.
    kept = row("10.1", "20000.00", claimed="6000.00")
    assert claim_total(kept) == D("6000.00")
    with pytest.raises(InputAboveBoundError):
        claim_total(row("10.1", "20000.00", claimed="6000.01"))


def test_a_class_10_1_row_without_the_flag_claims_nothing_when_no_property_is_left() -> None:
    # `cca_table`'s Class 10.1 has no flag: column 7 is positive with no property left, so the
    # maximum is 0.
    flagless = class_rates(classes=(CLASS_10_1,))
    capability = CcaClaim(flagless, CLASSES, CCA_CLAIM)

    assert capability.compute((classes(sold("0")),)).outputs[0].value == D("0")
    with pytest.raises(InputAboveBoundError):
        capability.compute((classes(sold("0.01")),))


def test_another_class_with_no_property_left_claims_nothing() -> None:
    other = row("8", "20000.00", proceeds="12000.00", claimed="0", no_property_left=1)
    assert claim_total(other) == D("0")
    with pytest.raises(InputAboveBoundError):
        claim_total(row("8", "20000.00", proceeds="12000.00", claimed="0.01", no_property_left=1))


def test_a_column_2_of_zero_allows_no_claim() -> None:
    # Bought and sold in the year: column 2 0, additions 30,000, proceeds 25,000, column 7 5,000.
    bought = row("10.1", "0", "30000", "25000", no_property_left=1)
    assert claim_total(bought) == D("0")
    with pytest.raises(InputAboveBoundError):
        claim_total(row("10.1", "0", "30000", "25000", claimed="0.01", no_property_left=1))


def test_a_negative_column_7_still_allows_the_claim_as_if_not_sold() -> None:
    # Column 7: 20,000.00 - 25,000.00 = -5,000.00; Regulation 1100(2.5) works the deduction as if
    # the vehicle had not been disposed of, so the maximum is still 3,000.00.
    negative = sold("3000.00", proceeds="25000.00")
    assert claim_total(negative) == D("3000.00")
    assert closing(negative) == [(D("10.1"), D("0"))]
    with pytest.raises(InputAboveBoundError):
        claim_total(sold("3000.01", proceeds="25000.00"))


def test_a_claim_after_column_22_is_limited_to_column_21_less_column_22() -> None:
    # Column 21 is 3,000.00; a column 22 of 500.00 leaves 2,500.00.
    capability = CcaClaimAfterColumn22(sale_class_rates(), CLASSES, NON_COMPLIANT, CCA_CLAIM)
    column_22 = non_compliant_cca(("10.1", "500.00"))

    (output,) = capability.compute((column_22, classes(sold("2500.00")))).outputs
    assert output.value == D("2500.00")
    with pytest.raises(InputAboveBoundError, match=r"above the maximum 2500.00"):
        capability.compute((column_22, classes(sold("2500.01"))))


# Column 7 below the sale's base amount: the maximum is not limited to column 7. Regulation
# 1100(2.5) works the deduction as if the vehicle had not been disposed of. Column 2 10,000.00
# gives column 19 5,000.00 and 1,500.00 at 30%.


def test_the_maximum_is_not_limited_to_column_7() -> None:
    # Proceeds 9,990.00: column 7 10.00, but the maximum is still 1,500.00.
    nearly_all = sold("1500.00", column_2="10000.00", proceeds="9990.00")

    assert claim_total(nearly_all) == D("1500.00")
    (line, _total) = claim_trace(nearly_all)
    assert (line.column_7, line.column_19, line.maximum) == (D("10.00"), D("5000.00"), D("1500.00"))
    assert closing(nearly_all) == [(D("10.1"), D("0"))]


def test_a_claim_above_the_maximum_is_refused_whatever_column_7_is() -> None:
    nearly_all = sold("1500.01", column_2="10000.00", proceeds="9990.00")

    with pytest.raises(InputAboveBoundError, match=r"^item 1: ca/cca_claimed 1500.01 is above the"):
        claim_total(nearly_all)
    with pytest.raises(InputAboveBoundError, match=r"above the maximum 1500.00"):
        closing(nearly_all)


def test_a_column_7_of_zero_still_allows_the_claim_as_if_not_sold() -> None:
    all_sold = sold("1500.00", column_2="10000.00", proceeds="10000.00")

    assert claim_total(all_sold) == D("1500.00")
    assert closing(all_sold) == [(D("10.1"), D("0"))]
    (line, _total) = claim_trace(all_sold)
    assert line.half_year_rule_on_sale is True
    assert line.maximum == D("1500.00")
    with pytest.raises(InputAboveBoundError):
        claim_total(sold("1500.01", column_2="10000.00", proceeds="10000.00"))


def test_a_claim_after_column_22_is_limited_by_the_maximum() -> None:
    # Maximum 1,500.00 less a column 22 of 4.00 leaves 1,496.00.
    capability = CcaClaimAfterColumn22(sale_class_rates(), CLASSES, NON_COMPLIANT, CCA_CLAIM)
    column_22 = non_compliant_cca(("10.1", "4.00"))
    nearly_all = dict(column_2="10000.00", proceeds="9990.00")

    (output,) = capability.compute((column_22, classes(sold("1496.00", **nearly_all)))).outputs
    assert output.value == D("1496.00")
    with pytest.raises(InputAboveBoundError, match=r"above the maximum 1496.00"):
        capability.compute((column_22, classes(sold("1496.01", **nearly_all))))


# --- the closing UCC ----------------------------------------------------------------------------


def test_the_closing_ucc_is_zero_whatever_is_claimed() -> None:
    # Row S: the 5,000.00 left after a claim of 3,000.00 is not deductible later (Regulation
    # 1100(2.5); Folio S3-F4-C1 paragraph 1.106), nor is the 8,000.00 left after no claim.
    assert closing(sold("3000.00")) == [(D("10.1"), D("0"))]
    assert closing(sold("0")) == [(D("10.1"), D("0"))]


def test_the_closing_ucc_refuses_a_claim_above_the_maximum() -> None:
    with pytest.raises(InputAboveBoundError):
        closing(sold("3000.01"))


def test_the_closing_ucc_of_a_row_with_additions_is_zero() -> None:
    # Row A: the 13,000.00 of column 7 less the 3,000.00 claim leaves 10,000.00, which closes at 0.
    assert closing(sold("3000.00", additions="5000")) == [(D("10.1"), D("0"))]


def test_the_closing_ucc_is_zero_for_a_column_2_of_zero() -> None:
    assert closing(row("10.1", "0", "30000", "25000", no_property_left=1)) == [(D("10.1"), D("0"))]


def test_the_closing_ucc_is_zero_for_a_negative_column_7() -> None:
    assert closing(sold("0", proceeds="25000.00")) == [(D("10.1"), D("0"))]


def test_the_closing_ucc_is_zero_for_another_class_with_no_property_left() -> None:
    other = row("8", "20000.00", proceeds="12000.00", no_property_left=1)
    assert closing(other) == [(D("8"), D("0"))]


# --- recapture and terminal loss ----------------------------------------------------------------


def test_there_is_no_terminal_loss_for_a_class_10_1_vehicle_sold() -> None:
    assert terminal_loss(sold("3000.00")) == Artifact(TERMINAL_LOSS, D("0"))


def test_there_is_no_recapture_for_a_class_10_1_vehicle_sold_with_a_positive_column_7() -> None:
    assert recapture(sold("3000.00")) == Artifact(RECAPTURED_CCA, D("0"))


def test_there_is_no_recapture_for_a_class_10_1_vehicle_sold_with_a_negative_column_7() -> None:
    assert recapture(sold("0", proceeds="25000.00")) == Artifact(RECAPTURED_CCA, D("0"))


def test_another_class_keeps_its_terminal_loss() -> None:
    # Class 1, column 7 5,000.00 with no property left: a terminal loss of 5,000.00.
    other = row("1", "20000", proceeds="15000", no_property_left=1)
    assert terminal_loss(other) == Artifact(TERMINAL_LOSS, D("5000"))


# --- the trace ----------------------------------------------------------------------------------


def test_traces_column_19_of_the_claim_as_the_half_year_rule_on_sale() -> None:
    # Row S: column 7 8,000.00; column 14 is 12,000.00 - 0 + 0 + 0; column 16 12,000.00; columns
    # 15, 17 and 18 0; column 19 10,000.00; maximum 3,000.00.
    assert claim_trace(sold("3000.00")) == (
        CcaClaimLine(
            output=CCA_CLAIM,
            position=1,
            class_rate=CLASS_10_1_ON_SALE,
            no_property_left=1,
            column_7=D("8000.00"),
            column_14=D("12000.00"),
            column_15=D("0"),
            column_16=D("12000.00"),
            column_17=D("0"),
            column_18=D("0"),
            column_19=D("10000.00"),
            zero_reason=CcaZeroReason.NONE,
            maximum=D("3000.00"),
            rounding=CENT,
            claim=D("3000.00"),
            half_year_rule_on_sale=True,
        ),
        ItemsTotalLine(CCA_CLAIM, ((1, D("3000.00")),), D("3000.00")),
    )


def test_a_row_without_the_rule_traces_it_as_not_used() -> None:
    kept = row("10.1", "20000.00", claimed="6000.00")
    other = row("8", "20000.00", claimed="4000.00")

    assert claim_trace(kept)[0].half_year_rule_on_sale is False
    assert claim_trace(other)[0].half_year_rule_on_sale is False


def test_a_class_10_1_row_with_a_column_2_of_zero_traces_the_rule_as_not_used() -> None:
    (line, _total) = claim_trace(row("10.1", "0", "30000", "25000", no_property_left=1))

    assert line.half_year_rule_on_sale is False
    assert line.zero_reason is CcaZeroReason.NO_PROPERTY_LEFT


def test_traces_the_closing_ucc_as_the_half_year_rule_on_sale() -> None:
    capability = ClosingUcc(sale_class_rates(), CLASSES, CLOSING_UCC)

    assert capability.compute((classes(sold("3000.00")),)).trace == (
        ClosingUccLine(
            CLOSING_UCC,
            1,
            CLASS_10_1_ON_SALE,
            1,
            D("8000.00"),
            CcaZeroReason.NONE,
            D("3000.00"),
            D("0"),
            half_year_rule_on_sale=True,
        ),
    )


def test_traces_the_terminal_loss_as_the_half_year_rule_on_sale() -> None:
    capability = TerminalLoss(sale_class_rates(), CLASSES, TERMINAL_LOSS)

    (line, total) = capability.compute((classes(sold("3000.00")),)).trace

    assert line == TerminalLossLine(
        output=TERMINAL_LOSS,
        position=1,
        class_rate=CLASS_10_1_ON_SALE,
        no_property_left=1,
        column_7=D("8000.00"),
        zero_reason=CcaZeroReason.NONE,
        column_7_positive=True,
        result=D("0"),
        half_year_rule_on_sale=True,
    )
    assert isinstance(total, ItemsTotalLine)
    assert total.total == D("0")


def test_the_closing_and_terminal_loss_lines_of_other_rows_trace_the_rule_as_not_used() -> None:
    other = row("1", "20000", proceeds="15000", no_property_left=1)
    (closing_line,) = (
        ClosingUcc(sale_class_rates(), CLASSES, CLOSING_UCC).compute((classes(other),)).trace
    )
    (loss_line, _total) = (
        TerminalLoss(sale_class_rates(), CLASSES, TERMINAL_LOSS).compute((classes(other),)).trace
    )

    assert isinstance(closing_line, ClosingUccLine)
    assert isinstance(loss_line, TerminalLossLine)
    assert closing_line.half_year_rule_on_sale is False
    assert loss_line.half_year_rule_on_sale is False


def test_the_claim_lines_of_two_classes_are_worked_each_on_its_own() -> None:
    plain = row("8", "10000", "3000", claimed="2300")

    (sale_line, plain_line, _total) = claim_trace(sold("3000.00"), plain)

    assert sale_line.half_year_rule_on_sale is True
    assert plain_line.half_year_rule_on_sale is False
    assert plain_line.maximum == D("2300.00")
