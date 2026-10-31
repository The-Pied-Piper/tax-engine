"""Which `core/apply_fraction` steps of the CA-ON manifest pass a blank base on.

Form T657 Step 3 says "If you tick Yes, complete the corresponding chart for that year", so a chart
not completed leaves its lines blank. The six steps whose base is a blank input of Charts 2021 to
2023 (the box 30 amounts of Part 1 line I and Part 2 line G) pass the blank on; no other
`core/apply_fraction` step names a blank rule yet.
"""

from __future__ import annotations

import tax_engine.jurisdictions.ca_on

# lists the packages; build_tax_computation registers their catalogs
import tax_engine.registrations
from tax_engine.adapters.outbound.yaml_jurisdictions import YamlJurisdictionSource
from tax_engine.domain.jurisdiction_code import JurisdictionCode
from tax_engine.domain.manifest import CapabilitySelection

CA_ON = JurisdictionCode("CA-ON")
BLANK_BASES = {
    f"ca/t657_chart_{year}_{base}"
    for year in (2021, 2022, 2023)
    for base in ("amount_i", "part_2_amount_g")
}


def apply_fraction_steps() -> list[CapabilitySelection]:
    (manifest,) = (
        YamlJurisdictionSource(tax_engine.registrations.JURISDICTIONS.roots())
        .get_jurisdiction(CA_ON)
        .manifests
    )
    return [
        step
        for form in manifest.forms
        for step in form.capabilities
        if step.name == "core/apply_fraction"
    ]


def test_the_six_blank_input_steps_pass_a_blank_base_on() -> None:
    passing = {step.consumes["base"]: step.blank for step in apply_fraction_steps() if step.blank}

    assert set(passing) == BLANK_BASES
    assert all(rule == {"base": "pass_on"} for rule in passing.values())


def test_no_other_apply_fraction_step_names_a_blank_rule() -> None:
    others = [step for step in apply_fraction_steps() if step.consumes["base"] not in BLANK_BASES]

    assert others
    assert all(not step.blank for step in others)
