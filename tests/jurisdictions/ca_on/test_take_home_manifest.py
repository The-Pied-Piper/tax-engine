"""The Ontario take-home manifest asks the caller for the gross salary and for nothing else.

The take-home calculator has one input. Every other input a form declares must be optional, with
its blank rule (a fixed fallback or `compute`), or a salary-only request is refused.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

import tax_engine.jurisdictions.ca_on
from tax_engine.adapters.outbound.yaml_jurisdictions import YamlJurisdictionSource
from tax_engine.domain.jurisdiction_code import JurisdictionCode
from tax_engine.domain.manifest import Manifest
from tax_engine.registrations import JURISDICTIONS, artifact_kinds, units
from tests.manifest_support import inputs_of

SALARY = "ca/employment_income"


def _manifest() -> Manifest:
    source = YamlJurisdictionSource(JURISDICTIONS.roots(), artifact_kinds(), units())
    (manifest,) = source.get_jurisdiction(JurisdictionCode("CA-ON")).manifests
    return manifest


def test_the_salary_is_the_only_required_input() -> None:
    required = {
        name for name, declaration in inputs_of(_manifest()).items() if declaration.required
    }

    assert required == {SALARY}


def test_the_return_exports_line_167_and_the_marginal_rate() -> None:
    # The federal marginal rate, the Ontario marginal rate and the health premium slope are read
    # inside the return by the final sum, so they are no longer exported (nor are the gates).
    (default,) = (form for form in _manifest().forms if form.name == "ca-on/return")

    assert set(default.exports) == {
        "ca-on/average_tax_rate",
        "ca-on/marginal_tax_rate",
        "ca/refund_or_balance_owing",
    }


EXACT = {"rounding": "ca-on/exact_rounding"}


def _band(
    table: str, base: str, output: str
) -> tuple[str, dict[str, str], dict[str, Any], dict[str, str]]:
    return ("core/amount_by_band_rate", {"table": table}, {"base": base}, {"output": output})


def _record_total(
    records: str, output: str
) -> tuple[str, dict[str, str], dict[str, Any], dict[str, str]]:
    return ("core/record_total", {}, {"records": records}, {"output": output})


def _rate_figure(
    rate: str, output: str
) -> tuple[str, dict[str, str], dict[str, Any], dict[str, str]]:
    return ("core/rate_figure", {"rate": rate}, {}, {"output": output})


def _multiply(
    base: str, rate: str, output: str
) -> tuple[str, dict[str, str], dict[str, Any], dict[str, str]]:
    return ("core/multiply_by_rate", EXACT, {"base": base, "rate": rate}, {"output": output})


def _subtract(
    amount: str, less: str, output: str
) -> tuple[str, dict[str, str], dict[str, Any], dict[str, str]]:
    return ("core/subtract", EXACT, {"amount": amount, "less": less}, {"output": output})


def _sum(
    parts: tuple[str, ...], output: str
) -> tuple[str, dict[str, str], dict[str, Any], dict[str, str]]:
    return ("core/sum", EXACT, {"parts": parts}, {"output": output})


# The steps of the return after the health premium slope: the four figures read from the federal
# form `ca/take_home_marginal_rates` (each its export, totalled by core/record_total), then the
# Ontario part of the marginal rate on the take-home basis, one capability per line, in order. The
# federal steps are pinned by the federal form's own tests; the last step here is the sum the
# take-home answer reads as the marginal rate.
MARGINAL_RATE_STEPS = [
    _record_total(
        "ca/take_home_marginal_rates.marginal_net_income_rate", "ca-on/marginal_net_income_rate"
    ),
    _record_total(
        "ca/take_home_marginal_rates.marginal_credit_contribution_rate",
        "ca-on/marginal_credit_contribution_rate",
    ),
    _record_total(
        "ca/take_home_marginal_rates.marginal_federal_rate", "ca-on/marginal_federal_rate"
    ),
    _record_total(
        "ca/take_home_marginal_rates.marginal_contribution_rate",
        "ca-on/marginal_contribution_rate",
    ),
    _rate_figure("ca-on/credit_rate", "ca-on/marginal_ontario_credit_rate"),
    _multiply(
        "ca-on/marginal_credit_contribution_rate",
        "ca-on/marginal_ontario_credit_rate",
        "ca-on/marginal_ontario_contribution_credit_rate",
    ),
    _multiply(
        "ca-on/ontario_bracket_rate_return",
        "ca-on/marginal_net_income_rate",
        "ca-on/marginal_ontario_bracket_rate",
    ),
    _subtract(
        "ca-on/marginal_ontario_bracket_rate",
        "ca-on/marginal_ontario_contribution_credit_rate",
        "ca-on/marginal_ontario_rate_after_credits",
    ),
    _multiply(
        "ca-on/ontario_surtax_factor",
        "ca-on/marginal_ontario_rate_after_credits",
        "ca-on/marginal_ontario_rate_with_surtax",
    ),
    _record_total(
        "ca-on/on428.on428_ontario_tax_reduction_line_80", "ca-on/ontario_tax_reduction_return"
    ),
    _band(
        "ca-on/marginal_rate_gate",
        "ca-on/ontario_tax_reduction_return",
        "ca-on/ontario_reduction_gate",
    ),
    _multiply(
        "ca-on/ontario_reduction_gate",
        "ca-on/marginal_ontario_rate_with_surtax",
        "ca-on/ontario_reduction_phase_out_rate",
    ),
    _sum(
        ("ca-on/marginal_ontario_rate_with_surtax", "ca-on/ontario_reduction_phase_out_rate"),
        "ca-on/marginal_ontario_rate_with_reduction",
    ),
    _record_total("ca-on/on428_a.lift_reduction", "ca-on/return_lift_reduction"),
    _record_total("ca-on/on428_a.lift_credit_single", "ca-on/return_lift_credit"),
    _band("ca-on/marginal_rate_gate", "ca-on/return_lift_reduction", "ca-on/lift_reduction_gate"),
    _band("ca-on/marginal_rate_gate", "ca-on/return_lift_credit", "ca-on/lift_credit_gate"),
    _multiply("ca-on/lift_reduction_gate", "ca-on/lift_credit_gate", "ca-on/lift_phase_out_gate"),
    _rate_figure("ca-on/lift_single_rate", "ca-on/lift_single_rate_figure"),
    _multiply(
        "ca-on/lift_phase_out_gate",
        "ca-on/lift_single_rate_figure",
        "ca-on/marginal_lift_reduction_rate",
    ),
    _multiply(
        "ca-on/marginal_lift_reduction_rate",
        "ca-on/marginal_net_income_rate",
        "ca-on/marginal_lift_phase_out_rate",
    ),
    _sum(
        ("ca-on/marginal_ontario_rate_with_reduction", "ca-on/marginal_lift_phase_out_rate"),
        "ca-on/marginal_ontario_rate_after_lift",
    ),
    _record_total(
        "ca-on/on428.on428_tax_after_lift_credit_line_86", "ca-on/ontario_tax_after_lift_return"
    ),
    _band(
        "ca-on/marginal_rate_gate", "ca-on/ontario_tax_after_lift_return", "ca-on/ontario_rate_gate"
    ),
    _multiply(
        "ca-on/marginal_ontario_rate_after_lift",
        "ca-on/ontario_rate_gate",
        "ca-on/ontario_marginal_rate",
    ),
    _multiply(
        "ca-on/return_health_premium_slope",
        "ca-on/marginal_net_income_rate",
        "ca-on/marginal_health_premium_rate",
    ),
    _sum(
        (
            "ca-on/marginal_federal_rate",
            "ca-on/ontario_marginal_rate",
            "ca-on/marginal_health_premium_rate",
            "ca-on/marginal_contribution_rate",
        ),
        "ca-on/marginal_tax_rate",
    ),
]


def test_the_return_calculates_the_take_home_marginal_rate_one_capability_per_line() -> None:
    # Every rate is read from a form figure or a dataset of the forms' rates; nothing runs twice.
    steps = _return_steps()
    start = [produces["output"] for *_, produces in steps].index(
        "ca-on/return_health_premium_slope"
    ) + 1

    assert steps[start:] == MARGINAL_RATE_STEPS


def test_the_return_exports_no_rate_part_but_line_167_and_the_marginal_rate() -> None:
    (default,) = (form for form in _manifest().forms if form.name == "ca-on/return")

    assert set(default.exports) == {
        "ca-on/average_tax_rate",
        "ca-on/marginal_tax_rate",
        "ca/refund_or_balance_owing",
    }


def test_the_t1_exports_line_42900_basic_federal_tax_for_the_return() -> None:
    (t1,) = (form for form in _manifest().forms if form.name == "ca/t1_tax_and_credits")

    assert "ca/federal_tax_after_credits" in t1.exports


def test_the_return_reads_the_federal_marginal_rate_form_instead_of_repeating_its_steps() -> None:
    # The federal facts (CPP, EI, the line 73 rate, the basic personal amount, the federal gate)
    # are in the `ca` package's form; the Ontario return holds none of them.
    steps = _return_steps()
    names = {name for *_, produces in steps for name in produces.values()}

    assert (
        not {
            "ca/federal_bracket_rate_return",
            "ca/federal_tax_after_credits_return",
            "ca/federal_rate_gate",
            "ca-on/marginal_cpp_base_rate",
            "ca-on/marginal_ei_rate",
            "ca-on/federal_bpa_phase_down_gate",
        }
        & names
    )
    assert [
        consumes["records"]
        for name, _, consumes, _ in steps
        if name == "core/record_total" and "take_home_marginal_rates" in consumes["records"]
    ] == [
        "ca/take_home_marginal_rates.marginal_net_income_rate",
        "ca/take_home_marginal_rates.marginal_credit_contribution_rate",
        "ca/take_home_marginal_rates.marginal_federal_rate",
        "ca/take_home_marginal_rates.marginal_contribution_rate",
    ]


def test_schedule_8_is_a_required_form_without_instances() -> None:
    (schedule_8,) = (form for form in _manifest().forms if form.name == "ca/schedule_8")

    assert schedule_8.required
    assert schedule_8.instances is None


def test_schedule_8_exports_the_cpp_figures_the_t1_and_on428_read() -> None:
    (schedule_8,) = (form for form in _manifest().forms if form.name == "ca/schedule_8")

    assert set(schedule_8.exports) == {
        "ca/schedule_8_cpp_base_contributions_on_return",
        "ca/schedule_8_cpp_enhanced_contributions_on_return",
        "ca/cpp_part_3_line_7_difference",
        "ca/cpp_part_3_line_4",
    }


def test_the_federal_forms_are_imported_in_the_order_the_manifest_lists_them() -> None:
    names = [form.name for form in _manifest().forms]

    imported = [
        "ca/t1_employment_income",
        "ca/t1_taxable_income",
        "ca/t1_tax_and_credits",
        "ca/t1_lines_copied_by_provinces",
        "ca/schedule_6",
        "ca/schedule_8",
        "ca/schedule_9",
        "ca/t2204",
        "ca/t691",
        "ca/take_home_marginal_rates",
    ]
    assert names[1 : 1 + len(imported)] == imported


def test_the_t1_reads_the_provincial_tax_ontario_supplies() -> None:
    (on428,) = (form for form in _manifest().forms if form.name == "ca-on/on428")

    assert dict(on428.supplies) == {"ca/provincial_tax.amount": "ca-on/on428_ontario_tax_line_90"}


def test_the_ontario_manifest_declares_the_federal_inputs_by_importing_their_forms() -> None:
    own = {
        path.name
        for path in Path(tax_engine.jurisdictions.ca_on.__file__).parent.rglob("*_inputs.yaml")
    }

    assert not {name for name in own if not name.startswith("on428_")}
    assert {
        "ca/cpp_months",
        "ca/other_employment_income",
        "ca/social_benefits_repayment",
    } <= set(inputs_of(_manifest()))


def test_on428_exports_lines_90_86_and_80_the_surtax_base_line_65_and_the_line_5_rate() -> None:
    (on428,) = (form for form in _manifest().forms if form.name == "ca-on/on428")

    assert set(on428.exports) == {
        "ca-on/on428_ontario_tax_line_90",
        "ca-on/on428_surtax_base_line_65",
        "ca-on/on428_bracket_column_rate_line_5",
        "ca-on/on428_tax_after_lift_credit_line_86",
        "ca-on/on428_ontario_tax_reduction_line_80",
    }


def test_on428_a_exports_the_line_19_reduction_and_the_line_20_credit() -> None:
    (on428_a,) = (form for form in _manifest().forms if form.name == "ca-on/on428_a")

    assert set(on428_a.exports) == {"ca-on/lift_credit_single", "ca-on/lift_reduction"}


def _return_steps() -> list[tuple[str, dict[str, str], dict[str, Any], dict[str, str]]]:
    """The steps of the return as (name, params, consumes, produces)."""
    (default,) = (form for form in _manifest().forms if form.name == "ca-on/return")
    return [
        (step.name, dict(step.params), dict(step.consumes), dict(step.produces))
        for step in default.capabilities
    ]


def test_the_return_reads_line_65_into_its_own_artifact_and_gives_the_surtax_factor() -> None:
    # The return totals the one amount of ON428's export of line 65 (the export of another form is
    # read as a record list) into its own artifact, then `ca-on/surtax_factor` reads that artifact
    # and the datasets of lines 66 and 67. Titles, references and units are not pinned here.
    steps = _return_steps()

    assert (
        "core/record_total",
        {},
        {"records": "ca-on/on428.on428_surtax_base_line_65"},
        {"output": "ca-on/ontario_surtax_base"},
    ) in steps
    assert (
        "ca-on/surtax_factor",
        {"line_66": "ca-on/surtax_line_66", "line_67": "ca-on/surtax_line_67"},
        {"base": "ca-on/ontario_surtax_base"},
        {"output": "ca-on/ontario_surtax_factor"},
    ) in steps


def test_the_return_reads_the_on428_line_5_bracket_rate() -> None:
    assert (
        "core/record_total",
        {},
        {"records": "ca-on/on428.on428_bracket_column_rate_line_5"},
        {"output": "ca-on/ontario_bracket_rate_return"},
    ) in _return_steps()


def test_the_return_still_totals_line_167() -> None:
    assert (
        "core/record_total",
        {},
        {"records": "ca/t1_tax_and_credits.refund_or_balance_owing"},
        {"output": "ca/refund_or_balance_owing"},
    ) in _return_steps()
