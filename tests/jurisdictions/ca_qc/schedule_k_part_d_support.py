"""Shared helpers of the Schedule K Part C line tests for lines 85 to 98.

Lines 85 to 98 read line 83 of Part C (line 84 is a copy of it) and boxes 60 to 62 of Part B.
Most tests give those four figures straight to the form (the form takes them as inputs), so a test
can pick the months without going through line 50. The salary tests run the real Part A, Part B and
Part C chains from a salary, for the default answer to line 50 (not covered) and for the answer yes
(covered). Every
figure below is hand-computed from the printed lines, not an official example.
"""

from __future__ import annotations

from decimal import Decimal
from textwrap import dedent
from typing import Any

import yaml

from tax_engine.domain.artifact import Artifact
from tax_engine.domain.jurisdiction_code import JurisdictionCode
from tax_engine.domain.kinds import AmountKind, CountKind
from tax_engine.domain.worksheet import Worksheet
from tax_engine.jurisdictions.ca_qc.catalog import (
    SCHEDULE_K_COLUMN_PREMIUM_LINE_83,
    SCHEDULE_K_GROUP_PLAN_COVERED_LINE_50,
    SCHEDULE_K_MONTHS_JANUARY_TO_JUNE_BOX_60,
    SCHEDULE_K_MONTHS_JULY_TO_DECEMBER_BOX_61,
    SCHEDULE_K_MONTHS_TOTAL_BOX_62,
)
from tests.jurisdictions.ca_qc.conftest import QUEBEC_PARTS, TakeHomeService
from tests.jurisdictions.ca_qc.schedule_k_part_c_support import PART_A, PART_C
from tests.jurisdictions.ca_qc.schedule_k_support import FORM_NAME, form_part, schedule_k_sheet

D = Decimal
PART_B = (
    "tp1_schedule_k_line_50_input.yaml",
    "tp1_schedule_k_line_50.yaml",
    "tp1_schedule_k_box_60.yaml",
    "tp1_schedule_k_box_61.yaml",
    "tp1_schedule_k_box_62.yaml",
)
# The Part C lines 85 to 98 in form order; a test takes the first parts up to the line it checks.
PART_D = (
    "tp1_schedule_k_line_85_months_in_year.yaml",
    "tp1_schedule_k_line_85.yaml",
    "tp1_schedule_k_line_86.yaml",
    "tp1_schedule_k_line_87.yaml",
    "tp1_schedule_k_line_88_box_60_amount.yaml",
    "tp1_schedule_k_line_88_box_60.yaml",
    "tp1_schedule_k_line_88_box_61_amount.yaml",
    "tp1_schedule_k_line_88_box_61.yaml",
    "tp1_schedule_k_line_88.yaml",
    "tp1_schedule_k_line_89.yaml",
    "tp1_schedule_k_line_90.yaml",
    "tp1_schedule_k_line_97_input.yaml",
    "tp1_schedule_k_line_98.yaml",
)
INPUTS = (
    SCHEDULE_K_COLUMN_PREMIUM_LINE_83,
    SCHEDULE_K_MONTHS_JANUARY_TO_JUNE_BOX_60,
    SCHEDULE_K_MONTHS_JULY_TO_DECEMBER_BOX_61,
    SCHEDULE_K_MONTHS_TOTAL_BOX_62,
)


def _steps(parts: tuple[str, ...]) -> list[dict[str, Any]]:
    """The capability steps of the real part files `parts`."""
    steps: list[dict[str, Any]] = []
    for part in parts:
        declared = yaml.safe_load((QUEBEC_PARTS / part).read_text("utf-8"))
        steps.extend(declared.get("capabilities") or [])
    return steps


def unconsumed(parts: tuple[str, ...]) -> tuple[str, ...]:
    """The kinds the real `parts` produce that no step of `parts` consumes: what a test form must
    export for the composition to be valid."""
    steps = _steps(parts)
    consumed: set[str] = set()
    for step in steps:
        for value in (step.get("consumes") or {}).values():
            consumed.update(value if isinstance(value, list) else [value])
    return tuple(
        step["produces"]["output"] for step in steps if step["produces"]["output"] not in consumed
    )


def header(parts: tuple[str, ...]) -> str:
    """A test header whose outputs are the line 83 and boxes 60 to 62 no part reads, or line 83 when
    every one is read."""
    consumed: set[str] = set()
    for step in _steps(parts):
        for value in (step.get("consumes") or {}).values():
            consumed.update(value if isinstance(value, list) else [value])
    left = [kind for kind in INPUTS if kind.identifier not in consumed] or [INPUTS[0]]
    outputs = "".join(f"  - {kind.identifier}\n" for kind in left)
    return (
        dedent("""\
        jurisdiction: CA-QC
        version: 1
        valid_from_tax_year: 2025
        """)
        + "outputs:\n"
        + outputs
    )


def form_declaration(parts: tuple[str, ...]) -> str:
    """The test form of Schedule K: its exports and the line 83 and boxes 60 to 62 inputs, which
    belong to the form that reads them."""
    inputs = "".join(f"  - name: {kind.identifier}\n    required: true\n" for kind in INPUTS)
    return form_part(unconsumed(parts)) + "inputs:\n" + inputs


# Printed lines 85 to 98 for a line 83, box 60 and box 61 given straight to the form (box 62 is
# their sum): (line 83, box 60, box 61) -> (85, 86, product of box 60, product of box 61, 88, 89,
# 90, 98). Line 85 is line 83 (line 84) times box 62 over 12, rounded once half-up to the cent.
# The products are box 60 times $62.00 and box 61 times $63.83. Line 90 is the lesser of lines 86
# and 89; line 98 is line 90 with a spouse premium of 0.
COLUMNS = {
    ("0.00", "0", "0"): ("0.00", "0.00", "0.00", "0.00", "0.00", "755.00", "0.00", "0.00"),
    ("766.00", "0", "0"): ("0.00", "766.00", "0.00", "0.00", "0.00", "755.00", "755.00", "755.00"),
    ("766.00", "6", "0"): (
        "383.00",
        "383.00",
        "372.00",
        "0.00",
        "372.00",
        "383.00",
        "383.00",
        "383.00",
    ),
    ("766.00", "6", "6"): ("766.00", "0.00", "372.00", "382.98", "754.98", "0.02", "0.00", "0.00"),
    ("392.00", "2", "1"): (
        "98.00",
        "294.00",
        "124.00",
        "63.83",
        "187.83",
        "567.17",
        "294.00",
        "294.00",
    ),
    ("744.80", "3", "2"): (
        "310.33",
        "434.47",
        "186.00",
        "127.66",
        "313.66",
        "441.34",
        "434.47",
        "434.47",
    ),
    ("766.00", "1", "0"): (
        "63.83",
        "702.17",
        "62.00",
        "0.00",
        "62.00",
        "693.00",
        "693.00",
        "693.00",
    ),
    ("0.01", "3", "3"): ("0.01", "0.00", "186.00", "191.49", "377.49", "377.51", "0.00", "0.00"),
}
# The same lines for the three salaries, by the answer to line 50: line 83 is 0.00, 766.00 and
# 766.00; the default answer (not covered, no months) and the answer yes (covered, 12 months).
SALARY_COLUMNS = {
    ("20000", "default"): ("0.00", "0.00", "0.00", "0.00", "0.00", "755.00", "0.00", "0.00"),
    ("20000", "yes"): ("0.00", "0.00", "372.00", "382.98", "754.98", "0.02", "0.00", "0.00"),
    ("70000", "default"): (
        "0.00",
        "766.00",
        "0.00",
        "0.00",
        "0.00",
        "755.00",
        "755.00",
        "755.00",
    ),
    ("70000", "yes"): ("766.00", "0.00", "372.00", "382.98", "754.98", "0.02", "0.00", "0.00"),
    ("200000", "default"): (
        "0.00",
        "766.00",
        "0.00",
        "0.00",
        "0.00",
        "755.00",
        "755.00",
        "755.00",
    ),
    ("200000", "yes"): ("766.00", "0.00", "372.00", "382.98", "754.98", "0.02", "0.00", "0.00"),
}
INDEX = {"85": 0, "86": 1, "p60": 2, "p61": 3, "88": 4, "89": 5, "90": 6, "98": 7}


def part_d(
    take_home_service: TakeHomeService, key: tuple[str, str, str], parts: tuple[str, ...]
) -> Worksheet:
    """The Schedule K worksheet of `parts` for a line 83 and boxes 60 and 61 given straight in."""
    line_84, box_60, box_61 = key
    (sheet,) = take_home_service(header(parts), form_declaration(parts), *parts).compute(
        JurisdictionCode("CA-QC"),
        2025,
        Artifact(SCHEDULE_K_COLUMN_PREMIUM_LINE_83, D(line_84)),
        Artifact(SCHEDULE_K_MONTHS_JANUARY_TO_JUNE_BOX_60, D(box_60)),
        Artifact(SCHEDULE_K_MONTHS_JULY_TO_DECEMBER_BOX_61, D(box_61)),
        Artifact(SCHEDULE_K_MONTHS_TOTAL_BOX_62, D(box_60) + D(box_61)),
    )[FORM_NAME]
    return sheet


def salary_sheet(
    take_home_service: TakeHomeService,
    salary: str,
    answer: str,
    parts: tuple[str, ...],
    *extra: tuple[AmountKind, str],
) -> Worksheet:
    """The Schedule K worksheet of Parts A and B, Part C to line 83 and the Part D `parts`, run
    from a salary; `answer` is "default" (line 50 left out) or "yes"; `extra` gives optional
    inputs."""
    given: list[tuple[AmountKind | CountKind, str]] = []
    if answer == "yes":
        given.append((SCHEDULE_K_GROUP_PLAN_COVERED_LINE_50, "1"))
    given.extend(extra)
    chain = PART_A + PART_B + PART_C + parts
    return schedule_k_sheet(take_home_service, salary, unconsumed(chain), chain, *given)
