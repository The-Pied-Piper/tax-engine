"""The printed titles of the Quebec 2025 optional inputs (#1919).

Each input stands for a line the form names. The title is the line's printed name (instruction
sentences and years left out); a line the form prints no name for has no title and is not listed.
Sources: Revenu Quebec TP-1.D-V (2025-12) and its Schedules B, F, K and P; CRA 5005-R (2025).
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

import pytest
import yaml

import tax_engine.jurisdictions.ca_qc

MANIFESTS = Path(tax_engine.jurisdictions.ca_qc.__file__).parent / "manifests/2025"
TITLES = {
    "ca-qc/schedule_b_line_12": ("Amount from line 275 of your spouse's return"),
    "ca-qc/schedule_b_lived_alone_line_20": (
        "You maintained and ordinarily lived in a dwelling in which you lived alone or only "
        "with one or more individuals under the age of 18, or with one or more of your "
        "children, grandchildren or great-grandchildren 18 or older who were full-time "
        "students pursuing vocational training at the secondary level or post-secondary "
        "studies"
    ),
    "ca-qc/schedule_b_line_33": ("Amount claimed on line 361 of your spouse's return"),
    "ca-qc/schedule_p_schedule_l_income_line_14": ("Total of lines 22 through 26.1 of Schedule L"),
    "ca-qc/schedule_p_deductible_income_line_22": (
        "Amount included in one of the above sources of income and entitling you to a "
        "deduction on line 293 of your return"
    ),
    "ca-qc/schedule_p_rl5_months_line_57": ("Total number of months in box V of your RL-5 slip"),
    "ca-qc/schedule_p_supplement_months_line_58": (
        "Number of months for which you meet the requirements for claiming the supplement to "
        "the work premium"
    ),
    "ca-qc/t1_line_41000": ("Federal political contribution tax credit"),
    "ca-qc/t1_line_41200": ("Investment tax credit"),
    "ca-qc/t1_line_41400": ("Labour-sponsored funds tax credit"),
    "ca-qc/t1_line_43700": ("Total income tax deducted"),
    "ca-qc/t1_line_43800": ("Tax transfer for residents of Quebec"),
    "ca-qc/t1_line_46800": ("Eligible educator school supply tax credit Supplies expenses"),
    "ca-qc/t1_line_24400": ("Canadian Armed Forces personnel and police deduction"),
    "ca-qc/t1_line_24900": ("Security options deductions"),
    "ca-qc/t1_line_25000": ("Other payments deduction"),
    "ca-qc/t1_line_25100": ("Limited partnership losses of other years"),
    "ca-qc/t1_line_25200": ("Non-capital losses of other years"),
    "ca-qc/t1_line_25300": ("Net capital losses of other years"),
    "ca-qc/t1_line_25395": (
        "Capital gains deduction for qualifying business transfers or qualifying cooperative "
        "conversions"
    ),
    "ca-qc/t1_line_25400": ("Capital gains deduction"),
    "ca-qc/t1_line_25500": ("Northern residents deductions"),
    "ca-qc/t1_line_25600": ("Additional deductions"),
    "ca-qc/t1_line_13500": ("Business income: Net"),
    "ca-qc/t1_line_13700": ("Professional income: Net"),
    "ca-qc/t1_line_13900": ("Commission income: Net"),
    "ca-qc/t1_line_14100": ("Farming income: Net"),
    "ca-qc/t1_line_14300": ("Fishing income: Net"),
    "ca-qc/t1_line_14400": ("Workers' compensation benefits"),
    "ca-qc/t1_line_14500": ("Social assistance payments"),
    "ca-qc/t1_line_14600": ("Net federal supplements paid"),
    "ca-qc/tp1_income_replacement_adjustment_line_358": (
        "Adjustment for income replacement indemnities"
    ),
    "ca-qc/tp1_line_390": (
        "Tax credit for volunteer firefighters and search and rescue volunteers"
    ),
    "ca-qc/tp1_line_391": ("Tax credit for career extension"),
    "ca-qc/tp1_line_392": ("Tax credit for recent graduates working in remote resource regions"),
    "ca-qc/tp1_line_395": ("Tax credits for donations and gifts"),
    "ca-qc/tp1_line_396": ("Home buyers' tax credit"),
    "ca-qc/tp1_line_398": ("Tax credit for tuition or examination fees"),
    "ca-qc/tp1_line_398_1": ("Tax credit for tuition or examination fees transferred by a child"),
    "ca-qc/tp1_line_105": ("Correction of employment income, if you received an RL-22 slip"),
    "ca-qc/tp1_line_107": ("Other employment income"),
    "ca-qc/tp1_line_110": ("Parental insurance benefits, RL-6 slip, box A"),
    "ca-qc/tp1_line_111": ("Employment Insurance benefits, T4E slip"),
    "ca-qc/tp1_line_114": ("Old Age Security pension, T4A(OAS) slip"),
    "ca-qc/tp1_line_119": ("QPP or CPP benefits, RL-2 slip, box C"),
    "ca-qc/tp1_line_122": (
        "Payments from a pension plan, an RRSP, a RRIF, a DPSP or a PRPP/VRSP, or annuities"
    ),
    "ca-qc/tp1_line_123": ("Retirement income transferred by your spouse"),
    "ca-qc/tp1_line_128": (
        "Dividends from taxable Canadian corporations, taxable amount of dividends"
    ),
    "ca-qc/tp1_line_130": ("Interest and other investment income"),
    "ca-qc/tp1_line_136": ("Rental income, net rental income"),
    "ca-qc/tp1_line_139": ("Taxable capital gains"),
    "ca-qc/tp1_line_142": ("Support payments received (taxable amount)"),
    "ca-qc/tp1_line_147": (
        "Social assistance payments, RL-5 slip, box A, and similar financial assistance, RL-5 "
        "slip, box B"
    ),
    "ca-qc/tp1_line_148": ("Income replacement indemnities and net federal supplements"),
    "ca-qc/tp1_line_154": ("Other income"),
    "ca-qc/tp1_line_164": ("Net business income"),
    "ca-qc/tp1_line_205": ("Registered pension plan (RPP) deduction, RL-1 slip, box D"),
    "ca-qc/tp1_line_207": ("Employment expenses and deductions"),
    "ca-qc/tp1_line_214": ("RRSP or PRPP/VRSP deduction, HBP or LLP"),
    "ca-qc/tp1_line_215": ("FHSA deduction"),
    "ca-qc/tp1_line_225": ("Support payments made (deductible amount)"),
    "ca-qc/tp1_line_228": ("Moving expenses"),
    "ca-qc/tp1_line_231": ("Carrying charges and interest expenses"),
    "ca-qc/tp1_line_234": ("Business investment loss"),
    "ca-qc/tp1_line_236": ("Deduction for residents of designated remote areas"),
    "ca-qc/tp1_line_241": ("Deduction for exploration and development expenses"),
    "ca-qc/tp1_line_245": (
        "Deduction for retirement income transferred to your spouse on December 31"
    ),
    "ca-qc/tp1_line_246": ("Deduction for a repayment of amounts overpaid to you"),
    "ca-qc/tp1_line_250": ("Other deductions"),
    "ca-qc/tp1_line_252": ("Carry-over of the adjustment of investment expenses"),
    "ca-qc/tp1_investment_expenses_adjustment_line_260": ("Adjustment of investment expenses"),
    "ca-qc/tp1_spouse_net_income_line_275": ("Amount from line 275 of your spouse's return"),
    "ca-qc/tp1_adjustment_of_deductions_line_276": ("Adjustment of deductions"),
    "ca-qc/tp1_benefit_and_disability_savings_income_line_278": (
        "Universal Child Care Benefit and income from a registered disability savings plan"
    ),
    "ca-qc/tp1_line_287": ("Deductions for strategic investments"),
    "ca-qc/tp1_line_289": ("Non-capital losses from other years"),
    "ca-qc/tp1_line_290": ("Net capital losses from other years"),
    "ca-qc/tp1_line_291": ("Capital gains deduction for a qualifying business transfer"),
    "ca-qc/tp1_line_292": ("Capital gains deduction"),
    "ca-qc/tp1_line_293": ("Deduction for income situated on a reserve"),
    "ca-qc/tp1_line_295": ("Deductions for certain income"),
    "ca-qc/tp1_line_297": ("Miscellaneous deductions"),
    "ca-qc/schedule_k_group_plan_covered_line_50": (
        "You were covered by basic prescription drug insurance provided by a group insurance "
        "plan of which you, your spouse, your father or your mother was a member, and this "
        "plan covered the cost of medications"
    ),
    "ca-qc/tp1_line_438": ("Annual registration fee for the enterprise register"),
    "ca-qc/tp1_line_439": (
        "QPIP premium on income from self-employment or employment outside Québec"
    ),
    "ca-qc/tp1_line_441": ("Advance payments of tax credits, RL-19 slip, box A, B, C, D, G or H"),
    "ca-qc/tp1_line_443": ("Special taxes and tax adjustment"),
    "ca-qc/tp1_line_445": ("QPP contribution on income from self-employment"),
    "ca-qc/tp1_line_451_3": ("Québec income tax withholding transferred by your spouse"),
    "ca-qc/tp1_line_452": ("QPP or CPP overpayment"),
    "ca-qc/tp1_line_453": ("Income tax paid in instalments"),
    "ca-qc/tp1_line_454": ("Transferable portion of the income tax withheld for another province"),
    "ca-qc/tp1_line_455": ("Tax credit for childcare expenses"),
    "ca-qc/tp1_line_458": ("Tax credit for home-support services for seniors"),
    "ca-qc/tp1_line_459": ("QST rebate for employees and partners"),
    "ca-qc/tp1_line_460": ("Tax shield"),
    "ca-qc/tp1_line_462": ("Other credits"),
    "ca-qc/tp1_line_463": ("Senior assistance tax credit"),
}


def _declared_titles() -> dict[str, Any]:
    titles: dict[str, Any] = {}
    for path in sorted(MANIFESTS.glob("*.yaml")):
        part = yaml.safe_load(path.read_text(encoding="utf-8"))
        if isinstance(part, dict):
            for declaration in part.get("inputs") or []:
                titles[declaration["name"]] = declaration.get("title")
    return titles


@pytest.mark.parametrize("name", sorted(TITLES))
def test_the_input_carries_the_printed_title_of_its_line(name: str) -> None:
    assert _declared_titles()[name] == TITLES[name]
