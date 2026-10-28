"""The CA-ON manifest entries of Schedule 12, the multigenerational home renovation tax credit (see
`test_manifest.py`)."""

from __future__ import annotations

from tax_calculator.domain.capabilities.apply_rate import ApplyRate
from tax_calculator.domain.manifest import CapabilitySelection
from tax_calculator.jurisdictions.ca.capabilities.home_renovation_line_3 import HomeRenovationLine3
from tax_calculator.jurisdictions.ca.capabilities.home_renovation_line_6 import HomeRenovationLine6
from tax_calculator.jurisdictions.ca.capabilities.home_renovation_line_7 import HomeRenovationLine7
from tax_calculator.jurisdictions.ca.catalog import (
    HOME_RENOVATION_LINE_3,
    HOME_RENOVATION_LINE_6,
    HOME_RENOVATION_LINE_8,
    HOME_RENOVATIONS,
    MULTIGENERATIONAL_HOME_RENOVATION_CREDIT,
)

INPUTS = frozenset({"ca/home_renovations"})

OUTPUTS = frozenset({"ca/home_renovation_line_3", "ca/home_renovation_line_6"})

STEPS = {
    # Schedule 12 Step 1, line 3 "Line 1 minus line 2 (maximum $50,000 per qualifying renovation)",
    # for each qualifying renovation (the caller's record): the total of the lines 3 over the
    # renovations, capped at line 4's maximum dataset.
    CapabilitySelection(
        name="ca/home_renovation_line_3",
        params={"maximum": "ca/home_renovation_maximum"},
        consumes={"renovations": "ca/home_renovations"},
        produces={"output": "ca/home_renovation_line_3"},
    ),
    # Schedule 12 Step 1, line 6 "Line 4 minus line 5", the maximum dataset less the amount
    # claimed by other eligible individuals, for each qualifying renovation.
    CapabilitySelection(
        name="ca/home_renovation_line_6",
        params={"maximum": "ca/home_renovation_maximum"},
        consumes={"renovations": "ca/home_renovations"},
        produces={"output": "ca/home_renovation_line_6"},
    ),
    # Schedule 12 Step 1, line 7 "Enter whichever is less: amount from line 3 or line 6. Your
    # qualifying expenditures for the qualifying renovation", and Step 2, line 8 (line 45354)
    # "Add the amounts from line 7 for each qualifying renovation. Your total qualifying
    # expenditures": the total of the lesser of lines 3 and 6 over the renovations.
    CapabilitySelection(
        name="ca/home_renovation_line_7",
        params={"maximum": "ca/home_renovation_maximum"},
        consumes={"renovations": "ca/home_renovations"},
        produces={"output": "ca/home_renovation_line_8"},
    ),
    # Schedule 12 Step 2, line 10 (line 45355) "Line 8 multiplied by the percentage from line 9"
    # "Applicable rate 14.5%": line 8 at the rate of its dataset, rounded half-up to the cent.
    CapabilitySelection(
        name="core/apply_rate",
        params={"rate": "ca/home_renovation_rate"},
        consumes={"base": "ca/home_renovation_line_8"},
        produces={"output": "ca/multigenerational_home_renovation_credit"},
    ),
}

WIRING = {
    (
        HomeRenovationLine3,
        frozenset({HOME_RENOVATIONS}),
        frozenset({HOME_RENOVATION_LINE_3}),
    ),
    (
        HomeRenovationLine6,
        frozenset({HOME_RENOVATIONS}),
        frozenset({HOME_RENOVATION_LINE_6}),
    ),
    (
        HomeRenovationLine7,
        frozenset({HOME_RENOVATIONS}),
        frozenset({HOME_RENOVATION_LINE_8}),
    ),
    (
        ApplyRate,
        frozenset({HOME_RENOVATION_LINE_8}),
        frozenset({MULTIGENERATIONAL_HOME_RENOVATION_CREDIT}),
    ),
}
