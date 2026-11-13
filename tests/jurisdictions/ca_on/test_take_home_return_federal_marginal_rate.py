"""Ontario return summary: the federal marginal rate, the bracket rate of the taxable income.

5006-R-25E, Step 5 Part A: each column of the federal tax
chart prints "Line 73: Rate" with 14.5%, 20.5%, 26%, 29% or 33%. The existing step
`ca/federal_bracket_column_rate_line_73` of `ca/t1_tax_and_credits` is the printed rate of the
column that line 70 falls in. The return summary reads it as a cross-form read: the T1 form exports
it, and one `core/record_total` step of `return.yaml` totals the one amount into the return's own
amount kind `ca/federal_marginal_rate`. The step has no printed title and no printed line, and
carries the unit `core/percent`, so the summary shows it untitled, with no reference, and a trace
prints the fraction 0.205 as the form prints it, "20.5%".

The test composes the real salary, Schedule 8, T1 taxable income, T2204, Schedule 6, ON428 parts and
the real T1 parts, as the line 167 test does. The header and the form are the real files:
`manifest.yaml` and `t1_tax_and_credits.yaml`. The salary is the only input. Ontario resident,
single filer, salary the only income, tax withheld 0, basic credits only.
"""

from __future__ import annotations

from decimal import Decimal

import pytest
import yaml

from tax_engine.adapters.inbound.trace_english import EnglishTraceRenderer
from tax_engine.adapters.outbound.yaml_jurisdictions import YamlJurisdictionSource
from tax_engine.adapters.outbound.yaml_parameters import YamlParameterSource
from tax_engine.application.services.tax_computation import TaxComputationService
from tax_engine.domain.artifact import Artifact
from tax_engine.domain.jurisdiction_code import JurisdictionCode
from tax_engine.domain.worksheet import Worksheet
from tax_engine.jurisdictions.ca.catalog.income import EMPLOYMENT_INCOME
from tax_engine.registrations import JURISDICTIONS, parameter_parsers, units
from tests.capabilities import bundled_capabilities
from tests.jurisdictions.ca_on.conftest import TAKE_HOME, TakeHomeService, header_without_imports
from tests.kinds import bundled_kinds, non_negative

D = Decimal
ONTARIO = JurisdictionCode("CA-ON")
T1_FORM = "ca/t1_tax_and_credits"
RETURN_FORM = "ca-on/return"
LINE_73 = "ca/federal_bracket_column_rate_line_73"
MARGINAL_RATE = "ca/federal_marginal_rate"
LINE_167 = "ca/refund_or_balance_owing"
# The real header and form, read from the take-home folder, not test-local: the manifest's header
# and the T1 tax and credits form declaration.
REAL_HEADER = header_without_imports()
REAL_FORM = next(TAKE_HOME.rglob("t1_tax_and_credits.yaml")).read_text(encoding="utf-8")
# The real parts composed beside the real header and form, as the line 167 test composes them: the
# return reads the T1 form's exports, so the chain up to line 167 is composed, then `return.yaml`.
PARTS = (
    "salary.yaml",
    *(part.name for part in sorted(TAKE_HOME.rglob("schedule_8*.yaml"))),
    *(part.name for part in sorted(TAKE_HOME.rglob("t2204*.yaml"))),
    "t1_taxable_income_inputs.yaml",
    "t1_taxable_income_line_15000.yaml",
    "t1_taxable_income_line_23300.yaml",
    "t1_taxable_income_line_23400.yaml",
    "t1_taxable_income_line_23600.yaml",
    "t1_taxable_income_line_23600_signed.yaml",
    "t1_taxable_income_line_25700_inputs.yaml",
    "t1_taxable_income_line_26000.yaml",
    "t1_taxable_income.yaml",
    "t1_taxable_income_line_10400_inputs.yaml",
    "t1_tax_and_credits_line_30000.yaml",
    "t1_tax_and_credits_line_76.yaml",
    "t1_tax_and_credits_line_31260.yaml",
    "t1_tax_and_credits_line_84.yaml",
    "t1_tax_and_credits_line_96.yaml",
    "t1_tax_and_credits_line_98.yaml",
    "t1_tax_and_credits_line_101.yaml",
    "t1_tax_and_credits_line_106.yaml",
    "t1_tax_and_credits_line_33500.yaml",
    "t1_tax_and_credits_line_33800.yaml",
    "t1_tax_and_credits_line_35000.yaml",
    "t1_tax_and_credits_line_125.yaml",
    "t1_tax_and_credits_line_40400.yaml",
    "t1_tax_and_credits_line_42900.yaml",
    "t1_tax_and_credits_line_128.yaml",
    "t1_tax_and_credits_line_40500_inputs.yaml",
    "t1_tax_and_credits_line_130.yaml",
    "t1_tax_and_credits_line_132.yaml",
    "t1_tax_and_credits_line_40600_inputs.yaml",
    "t1_tax_and_credits_line_40600.yaml",
    "t1_tax_and_credits_line_41600.yaml",
    "t1_tax_and_credits_line_41700.yaml",
    "t1_tax_and_credits_line_42000.yaml",
    *(part.name for part in sorted(TAKE_HOME.rglob("on428*.yaml"))),
    *(part.name for part in sorted(TAKE_HOME.rglob("schedule_6*.yaml"))),
    "t1_tax_and_credits_line_43500.yaml",
    "t1_tax_and_credits_line_48200.yaml",
    "t1_tax_and_credits_line_167.yaml",
    "return.yaml",
)


def _worksheets(
    take_home_service: TakeHomeService, salary: str
) -> dict[str, tuple[Worksheet, ...]]:
    """The worksheets of one run, keyed by form name, from the real header and form."""
    return take_home_service(REAL_HEADER, REAL_FORM, *PARTS).compute(
        ONTARIO, 2025, Artifact(EMPLOYMENT_INCOME, D(salary))
    )


def _summary(take_home_service: TakeHomeService, salary: str) -> Worksheet:
    """The return summary sheet, with the federal marginal rate on it."""
    (sheet,) = _worksheets(take_home_service, salary)[RETURN_FORM]
    return sheet


@pytest.mark.parametrize(
    ("salary", "rate"),
    [
        # $70,000: taxable income 69,335.00 falls in the 20.5% column.
        ("70000", "0.205"),
        # $20,000: the first bracket's rate, 14.5%.
        ("20000", "0.145"),
        # $275,000: taxable income 273,926.00 is in the top bracket, 33%.
        ("275000", "0.33"),
    ],
)
def test_the_federal_marginal_rate_is_the_line_73_rate_of_the_column(
    take_home_service: TakeHomeService, salary: str, rate: str
) -> None:
    summary = _summary(take_home_service, salary)

    assert summary.get(bundled_kinds().kind(MARGINAL_RATE)).value == D(rate)


@pytest.mark.parametrize("salary", ["10000", "20000", "70000", "100000", "150000", "275000"])
def test_the_federal_marginal_rate_equals_line_73_read_from_the_t1_sheet(
    take_home_service: TakeHomeService, salary: str
) -> None:
    worksheets = _worksheets(take_home_service, salary)
    (t1_sheet,) = worksheets[T1_FORM]
    (summary,) = worksheets[RETURN_FORM]
    kinds = bundled_kinds()

    assert summary.get(kinds.kind(MARGINAL_RATE)).value == t1_sheet.get(kinds.kind(LINE_73)).value


def test_the_return_summary_still_carries_line_167(take_home_service: TakeHomeService) -> None:
    summary = _summary(take_home_service, "70000")

    assert summary.get(bundled_kinds().kind(LINE_167)).value == D("11497.09")


def test_the_federal_marginal_rate_has_no_title_no_reference_and_the_percent_unit(
    take_home_service: TakeHomeService,
) -> None:
    summary = _summary(take_home_service, "70000")
    label = bundled_kinds().kind(MARGINAL_RATE).label

    assert summary.title(label) is None
    assert summary.reference(label) is None
    assert summary.unit(label) == units().get("core/percent")


def test_the_federal_marginal_rate_prints_as_the_percentage_the_form_prints(
    take_home_service: TakeHomeService,
) -> None:
    summary = _summary(take_home_service, "70000")

    lines = EnglishTraceRenderer().render_all(summary.trace, summary)

    assert any("gives 20.5%" in line for line in lines)


def test_the_real_t1_form_exports_include_line_167_and_the_line_73_rate() -> None:
    exports = yaml.safe_load(REAL_FORM)["form"]["exports"]

    assert {LINE_167, LINE_73} <= set(exports)


def test_the_real_ontario_manifest_computes_the_federal_marginal_rate_at_70000() -> None:
    # No fixture: the bundled Ontario manifest, with every take-home part, as the calculator loads.
    service = TaxComputationService(
        YamlJurisdictionSource(JURISDICTIONS.roots(), bundled_kinds(), units()),
        YamlParameterSource(JURISDICTIONS.roots(), parameter_parsers(), units()),
        bundled_capabilities(),
    )
    worksheets = service.compute(ONTARIO, 2025, Artifact(EMPLOYMENT_INCOME, D("70000")))
    (sheet,) = worksheets[RETURN_FORM]

    assert sheet.get(bundled_kinds().kind(MARGINAL_RATE)).value == D("0.205")


def test_the_federal_marginal_rate_kind_is_registered_non_negative_and_an_amount() -> None:
    kind = bundled_kinds().kind(MARGINAL_RATE)

    assert kind.identifier == MARGINAL_RATE
    assert kind.value_type is Decimal
    assert non_negative(kind) is True
