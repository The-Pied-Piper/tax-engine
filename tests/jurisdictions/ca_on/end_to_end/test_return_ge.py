"""CA-ON 2025 end to end: return ge, Form ON-BEN line 61080 with a spouse or common-law partner.

Return GE is `returns/2025_return_ge.yaml`: Return AJ's filer with a spouse or common-law partner on
December 31, 2025 whose net income of 48000 is higher, who ticks line 61080 (separate principal
residences for medical reasons). The tick is checked against the spouse fact: it may be 0 or 1, and
a 1 is refused for a filer with no spouse. The figures are chosen and worked out by hand from the
form text, as the description of the return shows; every line of the return, the Schedule ON428-A
Part B (LIFT) lines the spouse changes among them, is checked in the YAML, and the tests here pin
the tick's checks and outputs.
"""

from __future__ import annotations

import re
from typing import Any

import pytest

from tax_engine.domain.errors import InputAboveBoundError, InputBelowBoundError
from tax_engine.domain.worksheet import Worksheet
from tax_engine.jurisdictions.ca.catalog import (
    SPOUSE_OR_COMMON_LAW_PARTNER_ON_DECEMBER_31_TOTAL,
)
from tax_engine.jurisdictions.ca_on import catalog as ontario
from tests.jurisdictions.ca_on.end_to_end.support import compute_with_spouse


def return_ge(**overrides: Any) -> Worksheet:
    """Return GE's worksheet: the inputs of `returns/2025_return_ge.yaml`, unless overridden.

    Return AJ's filer (employment income of 30000, a deduction limit of 5400 and 3000 deducted),
    with a spouse or common-law partner on December 31 whose net income is 48000, the LIFT answered
    for a spouse at year end, and line 61080 ticked.
    """
    inputs: dict[str, Any] = {
        "income_tax_deducted": "3000",
        "spouse_or_common_law_partner_on_december_31": 1,
        "spouse_net_income": "48000",
        "spouse_net_income_before_adjustments": "48000",
        "separate_residences_for_medical_reasons": 1,
    }
    return compute_with_spouse(
        "48000", "30000", (), "0", "0", "5400", "0", "0", **{**inputs, **overrides}
    )


def test_a_tick_with_a_spouse_is_checked_and_carried_as_1() -> None:
    # Form ON-BEN line 61080: the tick is 1 and the spouse fact is 1, so the tick is checked to be
    # 0 or 1, then is at most the spouse count, which is 1 (`ca/count_at_least`), and the return
    # carries the tick with a spouse as 1.
    worksheet = return_ge()

    assert worksheet.get(SPOUSE_OR_COMMON_LAW_PARTNER_ON_DECEMBER_31_TOTAL).value == 1
    assert worksheet.get(ontario.SEPARATE_RESIDENCES_FOR_MEDICAL_REASONS).value == 1
    assert worksheet.get(ontario.SEPARATE_RESIDENCES_FOR_MEDICAL_REASONS_CHECKED).value == 1
    assert worksheet.get(ontario.SPOUSE_FOR_SEPARATE_RESIDENCES_CHECKED).value == 1


def test_no_tick_and_no_spouse_passes_with_the_output_0() -> None:
    # Line 61080 0 with no spouse: the check passes (0 is at most a count of 0), and the output
    # that carries the tick with a spouse is 0.
    worksheet = return_ge(
        spouse_or_common_law_partner_on_december_31=0,
        spouse_net_income="0",
        spouse_net_income_before_adjustments="0",
        separate_residences_for_medical_reasons=0,
    )

    assert worksheet.get(SPOUSE_OR_COMMON_LAW_PARTNER_ON_DECEMBER_31_TOTAL).value == 0
    assert worksheet.get(ontario.SEPARATE_RESIDENCES_FOR_MEDICAL_REASONS).value == 0
    assert worksheet.get(ontario.SEPARATE_RESIDENCES_FOR_MEDICAL_REASONS_CHECKED).value == 0
    assert worksheet.get(ontario.SPOUSE_FOR_SEPARATE_RESIDENCES_CHECKED).value == 0


def test_a_tick_of_1_with_no_spouse_is_refused_not_capped() -> None:
    # The spouse check is the count `ca/spouse_or_common_law_partner_on_december_31_total`, 0, and
    # line 61080 is at least that count only when the spouse is there: 1 is an input error.
    message = (
        "ca/spouse_or_common_law_partner_on_december_31_total 0 is below "
        "ca-on/separate_residences_for_medical_reasons_checked 1"
    )

    with pytest.raises(InputBelowBoundError, match=re.escape(message)):
        return_ge(
            spouse_or_common_law_partner_on_december_31=0,
            spouse_net_income="0",
            spouse_net_income_before_adjustments="0",
        )


def test_a_tick_of_2_is_refused_not_capped() -> None:
    # Form ON-BEN line 61080 is a tick box: a count of 2 is above a yes or no answer of 1, refused.
    message = "ca-on/separate_residences_for_medical_reasons 2 is above a yes or no answer of 1"

    with pytest.raises(InputAboveBoundError, match=re.escape(message)):
        return_ge(separate_residences_for_medical_reasons=2)


def test_a_spouse_without_a_tick_passes_and_the_output_is_the_spouse_count() -> None:
    # Line 61080 0 with a spouse: the tick is optional, so the check passes, and the output is the
    # spouse count of 1.
    worksheet = return_ge(separate_residences_for_medical_reasons=0)

    assert worksheet.get(ontario.SEPARATE_RESIDENCES_FOR_MEDICAL_REASONS_CHECKED).value == 0
    assert worksheet.get(ontario.SPOUSE_FOR_SEPARATE_RESIDENCES_CHECKED).value == 1
