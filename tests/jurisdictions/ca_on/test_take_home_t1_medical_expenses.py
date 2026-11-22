"""The T1 medical expenses form (5006-R, 2025, lines 33099 and 33199), as the parts wire it.

The form is its own, upstream of the T1 tax and credits form, because the provincial tax that form
reads would otherwise loop back into it. It names the form and exports lines 33099 and 33199.
AB428 line 44, BC428 line 46, MB428 line 43, SK428 line 43 and NL428 line 48 read line 33099, and
SK428 line 49 reads line 33199, instead of asking for the amount a second time. A salary-only
caller gives none, so each export holds 0.00.
"""

from __future__ import annotations

from decimal import Decimal
from textwrap import dedent

import yaml

from tax_engine.domain.artifact import Artifact
from tax_engine.domain.jurisdiction_code import JurisdictionCode
from tax_engine.jurisdictions.ca.catalog.income import EMPLOYMENT_INCOME
from tests.federal_forms import FEDERAL_FORMS, form_part_names
from tests.jurisdictions.ca_on.conftest import TakeHomeService
from tests.medical_support import medical_expenses, other_dependants_medical_expenses

D = Decimal
FORM = "ca/t1_medical_expenses"
EXPORT = "ca/medical_expenses_line_33099"
EXPORT_33199 = "ca/other_dependants_medical_expenses_line_33199"
EXPORTS = [EXPORT, EXPORT_33199]
HEADER = dedent("""\
    jurisdiction: CA-ON
    version: 1
    valid_from_tax_year: 2025
    outputs: []
    capabilities: []
    """)
PARTS = form_part_names("t1_employment_income", "t1_medical_expenses")


def test_the_form_is_the_t1_return_and_exports_lines_33099_and_33199() -> None:
    part = yaml.safe_load(
        (FEDERAL_FORMS / "t1_medical_expenses" / "t1_medical_expenses.yaml").read_text("utf-8")
    )

    assert part["form"]["name"] == FORM
    assert part["form"]["title"] == "T1 Income Tax and Benefit Return"
    assert part["form"]["exports"] == EXPORTS
    assert part["capabilities"] == []


def test_the_export_is_0_for_a_salary_only_caller_and_the_amount_to_the_cent_otherwise(
    take_home_service: TakeHomeService,
) -> None:
    service = take_home_service(HEADER, "{}\n", *PARTS)
    code = JurisdictionCode("CA-ON")
    (form,) = (f for f in service.compose(code, 2025).forms if f.name == FORM)
    assert [kind.identifier for kind in form.exports] == EXPORTS

    blank = service.compute(code, 2025, Artifact(EMPLOYMENT_INCOME, D("70000")))
    given = service.compute(
        code,
        2025,
        Artifact(EMPLOYMENT_INCOME, D("70000")),
        medical_expenses("1000.005"),
        other_dependants_medical_expenses("250.555"),
    )

    (blank_sheet,) = blank[FORM]
    (given_sheet,) = given[FORM]
    assert [blank_sheet.get(kind).value for kind in form.exports] == [D("0.00"), D("0.00")]
    assert [given_sheet.get(kind).value for kind in form.exports] == [D("1000.01"), D("250.56")]
