"""The solidarity tax credit's optional answers (Revenu Quebec TP-1.D.D-V (2025-12), Schedule D,
Part A) as the real input part declares them.

Line 12: "Did you live alone in a dwelling throughout 2025? (You are considered to have lived alone
if everyone you lived with was under 18.)" Lines 32 and 33 for a tenant or subtenant on December
31, 2025, lines 35 and 36 for an owner: the answer is tenant, subtenant or owner (1) or neither
(0), and the number of owners or tenants. A caller who gives no answer gets the default: not alone,
neither tenant nor owner, one owner or tenant (owner ruling 19 Nov 2026). The two yes or no answers
are checked by `ca/yes_or_no_count`, which refuses a count above 1.
"""

from __future__ import annotations

import pytest
import yaml

from tax_engine.domain.errors import InputAboveBoundError
from tax_engine.domain.kinds import CountKind
from tax_engine.jurisdictions.ca_qc.catalog import (
    SOLIDARITY_LIVED_ALONE_LINE_12,
    SOLIDARITY_OCCUPANTS_LINES_33_36,
    SOLIDARITY_TENANT_OR_OWNER_LINES_32_36,
)
from tests.jurisdictions.ca_qc.conftest import QUEBEC_PARTS, TakeHomeService
from tests.jurisdictions.ca_qc.solidarity_maximum_support import (
    ALONE,
    OCCUPANTS,
    TENANT,
    maximum_figure,
)
from tests.jurisdictions.ca_qc.support import quebec_kinds
from tests.kinds import non_negative

PART = QUEBEC_PARTS / "solidarity_credit_answers.yaml"
FORM = "ca-qc/solidarity_credit"


def test_the_part_declares_the_three_answers_with_their_defaults() -> None:
    part = yaml.safe_load(PART.read_text(encoding="utf-8"))

    assert list(part) == ["form", "inputs"]
    assert part["form"] == {"name": FORM}
    assert part["inputs"] == [
        {
            "name": ALONE,
            "title": "Did you live alone in a dwelling throughout 2025?",
            "reference": "12",
            "required": False,
            "default": "0",
            "basis": (
                "Did you live alone in a dwelling throughout 2025? (You are considered to have "
                "lived alone if everyone you lived with was under 18.)"
            ),
        },
        {
            "name": TENANT,
            "reference": "32 to 36",
            "required": False,
            "default": "0",
            "basis": "Tenant, subtenant or owner of your place of residence on December 31, 2025",
        },
        {
            "name": OCCUPANTS,
            "reference": "33 and 36",
            "required": False,
            "default": "1",
            "basis": "Number of owners or tenants of the dwelling",
        },
    ]


@pytest.mark.parametrize(
    "kind",
    [
        SOLIDARITY_LIVED_ALONE_LINE_12,
        SOLIDARITY_TENANT_OR_OWNER_LINES_32_36,
        SOLIDARITY_OCCUPANTS_LINES_33_36,
    ],
)
def test_the_kinds_are_registered_non_negative_counts(kind: CountKind) -> None:
    assert quebec_kinds().kind(kind.identifier) is kind
    assert isinstance(kind, CountKind)
    assert kind.value_type is int
    assert non_negative(kind)


@pytest.mark.parametrize(
    "identifier",
    [
        "ca-qc/solidarity_lived_alone_checked_line_12",
        "ca-qc/solidarity_housing_received",
        "ca-qc/solidarity_more_than_one_occupant",
    ],
)
def test_a_caller_who_gives_no_answer_gets_the_defaults(
    take_home_service: TakeHomeService, identifier: str
) -> None:
    assert maximum_figure(take_home_service, identifier) == 0


@pytest.mark.parametrize("answers", [{"alone": 2}, {"tenant": 2}])
def test_a_yes_or_no_answer_above_1_is_refused(
    take_home_service: TakeHomeService, answers: dict[str, int]
) -> None:
    with pytest.raises(InputAboveBoundError):
        maximum_figure(take_home_service, "ca-qc/solidarity_maximum_before_reduction", **answers)
