"""Shared helpers of the Quebec return summary tests: the real return part over the real chains it
reads (5005-R, TP-1 totals and the solidarity credit).

The header is the real manifest header (the return's identity, its federal imports and its outputs)
with the four TP-1 slip figures that Schedule U reads added as plain starting inputs, as in the
other TP-1 tests. The salary is $20,000, $70,000 and $200,000; every optional input is left out and
the three optional answers take their defaults (not alone, neither tenant nor owner, not covered
by a group drug plan). The expected figures are hand-computed from the printed lines, not a CRA
or Revenu Quebec example.
"""

from __future__ import annotations

from decimal import Decimal
from typing import Any

from tax_engine.domain.artifact import Artifact
from tax_engine.domain.jurisdiction_code import JurisdictionCode
from tax_engine.domain.worksheet import Worksheet
from tests.jurisdictions.ca_qc.basic_personal_amount_support import FORM as T1_FORM
from tests.jurisdictions.ca_qc.basic_personal_amount_support import PARTS as T1_PARTS
from tests.jurisdictions.ca_qc.conftest import TakeHomeService
from tests.jurisdictions.ca_qc.solidarity_maximum_support import ANSWERS_PART
from tests.jurisdictions.ca_qc.support import MANIFEST
from tests.jurisdictions.ca_qc.tp1_net_income_support import HEADER, slip_artifacts
from tests.jurisdictions.ca_qc.tp1_totals_support import ALL_PARTS, CHAIN_PARTS
from tests.jurisdictions.ca_qc.tp1_totals_support import EXPECTED as TOTALS_EXPECTED

D = Decimal
# The slip inputs of the TP-1 net income header, without its outputs.
SLIP_INPUTS = HEADER[HEADER.index("inputs:") : HEADER.index("outputs:")]
RETURN_PART = "return.yaml"
# The solidarity credit parts, over the TP-1 net income lines the family income reads.
SOLIDARITY_PARTS = (
    "solidarity_credit_amounts.yaml",
    ANSWERS_PART,
    "solidarity_credit_maximum.yaml",
    "solidarity_credit_family_income.yaml",
    "solidarity_credit_reduction.yaml",
)
# The T1 chain, the TP-1 totals chain, the solidarity chain and the return part, each part once.
PARTS = tuple(
    dict.fromkeys(
        (
            *(part for part in T1_PARTS if part != "salary.yaml"),
            *CHAIN_PARTS,
            "tp1_totals.yaml",
            *ALL_PARTS,
            *SOLIDARITY_PARTS,
            "solidarity_credit.yaml",
            RETURN_PART,
        )
    )
)

# The printed lines the return adds, at each salary, default answers (not alone, neither tenant nor
# owner, not covered by a group drug plan, so the 755.00 premium is on TP-1 line 447 at $70,000 and
# $200,000): 5005-R line 172, line 43500 and line 44000, and the solidarity credit (July 2026 to
# June 2027). TP-1 lines 450 and 456 are the totals support's. Line 172 is line 43500 less line
# 44000 less the Canada workers benefit (45300, 2,679.07 at $20,000).
EXPECTED: dict[str, dict[str, str]] = {
    salary: {
        **TOTALS_EXPECTED[salary],
        **printed,
    }
    for salary, printed in {
        "20000": {"172": "-2560.02", "43500": "142.57", "44000": "23.52", "solidarity": "363.00"},
        "70000": {"172": "6282.16", "43500": "7523.55", "44000": "1241.39", "solidarity": "0.00"},
        "200000": {
            "172": "32886.26",
            "43500": "39384.74",
            "44000": "6498.48",
            "solidarity": "0.00",
        },
    }.items()
}


def header() -> str:
    """The real manifest header with the TP-1 slip figures added as starting inputs."""
    text = MANIFEST.read_text(encoding="utf-8")
    return text.replace("title: Return summary\n", "title: Return summary\n" + SLIP_INPUTS)


def return_sheet(
    take_home_service: TakeHomeService, salary: str, *given: Artifact[Any]
) -> Worksheet:
    """The return summary worksheet for a salary, over the real chains; every optional input is
    left out unless in `given`."""
    starting = [*slip_artifacts(salary), *given]
    service = take_home_service(header(), T1_FORM, *PARTS)
    (sheet,) = service.compute(JurisdictionCode("CA-QC"), 2025, *starting)["ca-qc/return"]
    return sheet
