"""T1 General 2025 (5006-R, Ontario) line 167 "Refund or balance owing", from the salary alone.

5006-R-25E: "Line 167: Line 149 minus line 166 If the amount
is negative, enter it on line 48400 below. If the amount is positive, enter it on line 48500 below.
Refund or balance owing". Line 149 is line 43500 "Total payable" (`ca/total_payable`) and line 166
is line 48200 "Total credits" (`ca/total_credits`), so line 167 is `core/subtract` of the two:
`ca/total_credits` taken off `ca/total_payable`, rounded once to the cent by `ca/cent_rounding`, and
produces the existing signed kind `ca/refund_or_balance_owing`. The figure has no floor: a negative
figure is a refund (line 48400), a positive one a balance owing (line 48500). Lines 48400 and 48500
are left out as sign routing: the sign of line 167 only routes the figure to one of
them, and neither line is computed here.

The test composes the real salary, Schedule 8, T1 taxable income, T2204, Schedule 6, ON428 parts,
the real line 42000 chain, and the parts of lines 43500, 48200 and the part under test. The header
and the form are the real files: `manifest.yaml` and `t1_tax_and_credits.yaml`.
The salary is the only input. Ontario resident, single filer, salary the only income, tax withheld
0, basic credits only.
"""

from __future__ import annotations

from decimal import Decimal

import pytest
import yaml

from tax_engine.adapters.inbound.trace_english import EnglishTraceRenderer
from tax_engine.adapters.outbound.yaml_jurisdictions import YamlJurisdictionSource
from tax_engine.adapters.outbound.yaml_parameters import YamlParameterSource
from tax_engine.application.models.calculation_request import TaxCalculationRequest
from tax_engine.application.services.tax_computation import TaxComputationService
from tax_engine.domain.artifact import Artifact
from tax_engine.domain.jurisdiction_code import JurisdictionCode
from tax_engine.domain.worksheet import Worksheet
from tax_engine.jurisdictions.ca.catalog.income import EMPLOYMENT_INCOME
from tax_engine.registrations import JURISDICTIONS, parameter_parsers, units
from tests.capabilities import bundled_capabilities
from tests.federal_forms import form_part_names
from tests.jurisdictions.ca_on.conftest import TAKE_HOME, TakeHomeService, header_without_imports
from tests.kinds import bundled_kinds, non_negative

D = Decimal
ONTARIO = JurisdictionCode("CA-ON")
FORM = "ca/t1_tax_and_credits"
LINE_43500 = "ca/total_payable"
FEDERAL_TAX_AFTER_CREDITS = "ca/federal_tax_after_credits"
LINE_48200 = "ca/total_credits"
LINE_167 = "ca/refund_or_balance_owing"
FEDERAL_TAX_ON_TAXABLE_INCOME_LINE_76 = "ca/federal_tax_on_taxable_income_line_76"
FEDERAL_BRACKET_COLUMN_RATE_LINE_73 = "ca/federal_bracket_column_rate_line_73"
# The real header and form, read from the take-home folder, not test-local: the manifest's header
# and the T1 tax and credits form declaration.
REAL_HEADER = header_without_imports()
REAL_FORM = next(TAKE_HOME.rglob("t1_tax_and_credits.yaml")).read_text(encoding="utf-8")
# The real parts composed beside the real header and form: the salary, the real Schedule 8, Schedule
# 6, T2204 and ON428 parts, the real T1 taxable-income lines and inputs, lines 30000, 76, 84, 31260,
# 96, 98, 101, 106, 33500, 33800, 35000, 40400, 125, 42900, 128, 130 and 132, lines 40600 and 41600
# with the input of line 40600, lines 40500 and 40600 inputs, line 41700, line 42000, then the parts
# of line 43500, line 48200 and the part under test.
PARTS = (
    *form_part_names("t1_lines_copied_by_provinces"),
    *form_part_names("t691"),
    *form_part_names("schedule_8"),
    *form_part_names("schedule_9"),
    *form_part_names("t2204"),
    *form_part_names("take_home_average_rate"),
    *form_part_names("take_home_marginal_rates"),
    *form_part_names("t1_taxable_income", "t1_employment_income"),
    "t1_tax_and_credits_line_30000.yaml",
    "t1_tax_and_credits_line_76.yaml",
    "t1_tax_and_credits_line_31260.yaml",
    "t1_tax_and_credits_line_78_worksheet_lines_1_to_3.yaml",
    "t1_tax_and_credits_line_78_worksheet_lines_4_to_7.yaml",
    "t1_tax_and_credits_line_78.yaml",
    "t1_tax_and_credits_line_84.yaml",
    "t1_tax_and_credits_line_96.yaml",
    "t1_tax_and_credits_line_98.yaml",
    "t1_tax_and_credits_line_101.yaml",
    "t1_tax_and_credits_line_106.yaml",
    "t1_tax_and_credits_line_107.yaml",
    "t1_tax_and_credits_line_108.yaml",
    "t1_tax_and_credits_line_109.yaml",
    "t1_tax_and_credits_line_110.yaml",
    "t1_tax_and_credits_line_111.yaml",
    "t1_tax_and_credits_line_33200.yaml",
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
    *form_part_names("schedule_6"),
    "t1_tax_and_credits_line_43500.yaml",
    "t1_tax_and_credits_line_47900.yaml",
    "t1_tax_and_credits_line_48200.yaml",
    "t1_tax_and_credits_line_167.yaml",
    "return.yaml",
)


def _worksheets(
    take_home_service: TakeHomeService, salary: str
) -> dict[str, tuple[Worksheet, ...]]:
    """The worksheets of one run, keyed by form name, from the real header and form."""
    return take_home_service(REAL_HEADER, REAL_FORM, *PARTS).compute(
        TaxCalculationRequest(ONTARIO, 2025, (Artifact(EMPLOYMENT_INCOME, D(salary)),))
    )


def _sheet(take_home_service: TakeHomeService, salary: str) -> Worksheet:
    """The tax and credits sheet, with lines 43500, 48200 and 167 on it."""
    (sheet,) = _worksheets(take_home_service, salary)[FORM]
    return sheet


@pytest.mark.parametrize(
    ("salary", "line_43500", "line_48200", "line_167"),
    [
        # $70,000: line 43500 is 11,497.09 and line 48200 is 0.00 (the CWB is fully reduced), so
        # line 167 is 11,497.09: a balance owing.
        ("70000", "11497.09", "0.00", "11497.09"),
        # $20,000: line 43500 is 158.09 and line 48200 is 1,633.00 (the CWB), so line 167 is
        # -1,474.91: the credits are larger, and the negative figure is a refund.
        ("20000", "158.09", "1633.00", "-1474.91"),
    ],
)
def test_line_167_is_line_43500_less_line_48200(
    take_home_service: TakeHomeService,
    salary: str,
    line_43500: str,
    line_48200: str,
    line_167: str,
) -> None:
    sheet = _sheet(take_home_service, salary)
    kinds = bundled_kinds()

    refund_or_balance_owing = sheet.get(kinds.kind(LINE_167)).value
    assert refund_or_balance_owing == D(line_167)
    assert refund_or_balance_owing.as_tuple().exponent == -2
    assert sheet.get(kinds.kind(LINE_43500)).value == D(line_43500)
    assert sheet.get(kinds.kind(LINE_48200)).value == D(line_48200)


@pytest.mark.parametrize("salary", ["20000", "70000"])
def test_line_167_equals_line_43500_less_line_48200_read_from_the_sheet(
    take_home_service: TakeHomeService, salary: str
) -> None:
    sheet = _sheet(take_home_service, salary)
    kinds = bundled_kinds()
    line_43500 = sheet.get(kinds.kind(LINE_43500)).value
    line_48200 = sheet.get(kinds.kind(LINE_48200)).value

    assert sheet.get(kinds.kind(LINE_167)).value == line_43500 - line_48200


def test_line_167_names_line_43500_line_48200_and_its_rounding_in_the_trace(
    take_home_service: TakeHomeService,
) -> None:
    sheet = _sheet(take_home_service, "70000")

    assert (
        "Line 43500 (CA$11497.09) less line 48200 (CA$0.00) gives CA$11497.09 "
        "(rounded to the nearest cent)."
    ) in EnglishTraceRenderer().render_all(sheet.trace, sheet)


def test_the_real_t1_form_header_exports() -> None:
    # Line 76 is read inside the form by line 40400 only, so it is not exported.
    exports = yaml.safe_load(REAL_FORM)["form"]["exports"]

    assert set(exports) == {
        LINE_167,
        LINE_43500,
        FEDERAL_BRACKET_COLUMN_RATE_LINE_73,
        FEDERAL_TAX_AFTER_CREDITS,
        "ca/ei_overpayment_line_45000",
        "ca/cwb_line_45300",
        "ca/provincial_credits_line_47900",
    }
    assert FEDERAL_TAX_ON_TAXABLE_INCOME_LINE_76 not in exports


def test_the_real_ontario_manifest_computes_refund_or_balance_owing_at_70000() -> None:
    # No fixture: the bundled Ontario manifest, with every take-home part, as the calculator loads.
    service = TaxComputationService(
        YamlJurisdictionSource(JURISDICTIONS.roots(), bundled_kinds(), units()),
        YamlParameterSource(JURISDICTIONS.roots(), parameter_parsers(), units()),
        bundled_capabilities(),
    )
    worksheets = service.compute(
        TaxCalculationRequest(ONTARIO, 2025, (Artifact(EMPLOYMENT_INCOME, D("70000")),))
    )
    (sheet,) = worksheets[FORM]

    assert sheet.get(bundled_kinds().kind(LINE_167)).value == D("11497.09")


def test_the_refund_or_balance_owing_kind_is_registered_and_signed() -> None:
    kind = bundled_kinds().kind(LINE_167)

    assert kind.identifier == LINE_167
    assert non_negative(kind) is False
