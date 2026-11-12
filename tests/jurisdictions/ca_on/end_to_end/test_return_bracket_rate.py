"""The Ontario return summary carries the ON428 line 5 bracket column rate, through the real engine.

The return summary gives the Ontario bracket rate. No new form text: the rate is the one printed
in the column of the ON428 chart (line 5), the existing step
`ca-on/on428_bracket_column_rate_line_5` ("Line 5: Rate 5.05%", "9.15%", "11.16%", "12.16%",
"13.16%", CRA 5006-c-25e.txt).

Another form reads an export only as a record list, as the return does for T1 line 167. So the
ON428 form exports line 5 and the return summary has one `core/record_total` step consuming
`ca-on/on428.on428_bracket_column_rate_line_5`, producing the Ontario kind
`ca-on/ontario_bracket_rate_return` (a non-negative amount, unit `core/percent`). The default
form `ca-on/return` lists it in its outputs beside `ca/refund_or_balance_owing`.

Figures (the real bundled manifest, salary the only input): $20,000 gives the first bracket's rate
0.0505, $70,000 gives 0.0915 and $275,000 gives the top bracket's rate 0.1316. The $70,000
take-home stays 53,468.68 (salary less CPP, EI and total tax, done outside the engine as the
README says).
"""

from __future__ import annotations

from decimal import Decimal

import pytest

from tax_engine.adapters.outbound.yaml_jurisdictions import YamlJurisdictionSource
from tax_engine.domain.artifact import Artifact
from tax_engine.domain.jurisdiction_code import JurisdictionCode
from tax_engine.domain.manifest import Manifest
from tax_engine.domain.worksheet import Worksheet
from tax_engine.jurisdictions.ca.catalog.income import EMPLOYMENT_INCOME
from tax_engine.registrations import JURISDICTIONS, units
from tests.jurisdictions.ca_on.conftest import TAKE_HOME, TakeHomeService, header_without_imports
from tests.kinds import bundled_kinds, non_negative

D = Decimal
ONTARIO = JurisdictionCode("CA-ON")
RETURN = "ca-on/return"
ON428 = "ca-on/on428"
LINE_5 = "ca-on/on428_bracket_column_rate_line_5"
RETURN_RATE = "ca-on/ontario_bracket_rate_return"
LINE_167 = "ca/refund_or_balance_owing"


HEADER = header_without_imports()
RETURN_FORM = (TAKE_HOME / "return.yaml").read_text(encoding="utf-8")
PARTS = (
    "salary.yaml",
    *(
        part.name
        for part in sorted(TAKE_HOME.rglob("*.yaml"))
        if part.name not in {"manifest.yaml", "return.yaml", "salary.yaml"}
    ),
)


def _manifest() -> Manifest:
    source = YamlJurisdictionSource(JURISDICTIONS.roots(), bundled_kinds(), units())
    (manifest,) = source.get_jurisdiction(ONTARIO).manifests
    return manifest


def _worksheets(
    take_home_service: TakeHomeService, salary: str
) -> dict[str, tuple[Worksheet, ...]]:
    service = take_home_service(HEADER, RETURN_FORM, *PARTS)
    return service.compute(ONTARIO, 2025, Artifact(EMPLOYMENT_INCOME, D(salary)))


def test_the_on428_form_exports_the_bracket_column_rate_of_line_5() -> None:
    (on428,) = (form for form in _manifest().forms if form.name == ON428)

    assert LINE_5 in on428.exports


def test_the_return_lists_the_bracket_rate_and_the_refund_or_balance_owing() -> None:
    (default,) = (form for form in _manifest().forms if form.name == RETURN)

    assert {RETURN_RATE, LINE_167} <= set(default.exports)


def test_the_return_bracket_rate_kind_is_a_registered_non_negative_amount() -> None:
    kind = bundled_kinds().kind(RETURN_RATE)

    assert kind.identifier == RETURN_RATE
    assert non_negative(kind)


@pytest.mark.parametrize(
    ("salary", "rate"),
    [
        # $20,000: taxable income 19,835.00 is in column 1, the first bracket, 5.05%.
        ("20000", "0.0505"),
        # $70,000: taxable income 69,335.00 is in column 2, 9.15%.
        ("70000", "0.0915"),
        # $275,000: taxable income is above 220,000, the top column, 13.16%.
        ("275000", "0.1316"),
    ],
)
def test_the_return_bracket_rate_is_the_line_5_rate(
    take_home_service: TakeHomeService, salary: str, rate: str
) -> None:
    worksheets = _worksheets(take_home_service, salary)
    kinds = bundled_kinds()
    (on428,) = worksheets[ON428]
    (summary,) = worksheets[RETURN]

    assert on428.get(kinds.kind(LINE_5)).value == D(rate)
    assert summary.get(kinds.kind(RETURN_RATE)).value == D(rate)


def test_the_70000_take_home_stays_53468_68(take_home_service: TakeHomeService) -> None:
    worksheets = _worksheets(take_home_service, "70000")
    kinds = bundled_kinds()
    (summary,) = worksheets[RETURN]
    (schedule_8,) = worksheets["ca/schedule_8"]
    (t2204,) = worksheets["ca/t2204"]
    total_tax = summary.get(kinds.kind(LINE_167)).value
    cpp = sum(
        (
            schedule_8.get(kinds.kind(name)).value
            for name in (
                "ca/schedule_8_cpp_base_contributions_on_return",
                "ca/schedule_8_cpp_enhanced_contributions_on_return",
            )
        ),
        D("0"),
    )
    ei = t2204.get(kinds.kind("ca/t2204_premiums_deducted")).value

    assert total_tax == D("11497.09")
    assert D("70000") - cpp - ei - total_tax == D("53468.68")


def test_the_return_prints_the_bracket_rate_as_a_percentage_in_the_core_percent_unit(
    take_home_service: TakeHomeService,
) -> None:
    (summary,) = _worksheets(take_home_service, "70000")[RETURN]

    unit = summary.unit(bundled_kinds().kind(RETURN_RATE).label)

    assert unit is not None
    assert unit.identifier == "core/percent"
