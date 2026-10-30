"""Unit tests for the layout of the trace packages: each line class's home module.

The generic line classes live in `tax_engine.domain.trace`, one module per feature group, each
with an
`__all__`; its `__init__` re-exports every module's `__all__`, so
`from tax_engine.domain.trace import SumLine` keeps working. Every exported line class appears
in
`HOMES`, so a new one is placed deliberately. A jurisdiction's own trace package is checked under
`tests/jurisdictions/<package>/test_trace_modules.py`.
"""

from __future__ import annotations

import importlib
import inspect

import pytest

import tax_engine.domain.trace
from tax_engine.domain.trace import TraceLine

CORE = "tax_engine.domain.trace"

CORE_HOMES: dict[str, tuple[str, ...]] = {
    "base": ("TraceLine",),
    "blank": ("LeftBlankLine", "BlankFallbackLine", "BlankPassedOnLine"),
    "arithmetic": (
        "RoundedTotalLine",
        "SumLine",
        "SumNotBelowZeroLine",
        "RateAppliedLine",
        "DividedByRateLine",
        "SignChosenDifferenceLine",
        "SubtractedLine",
        "SubtractedNotBelowZeroLine",
        "CreditAmountLine",
        "CappedAmountLine",
        "LesserOfLine",
        "LesserOfWithMaximumLine",
        "GreaterOfLine",
        "PerUnitAmountLine",
        "MultipleOverLine",
        "AtMostLine",
        "ClaimAtMostLine",
        "FractionAppliedLine",
        "PercentageAppliedLine",
        "RatioAppliedLine",
        "TimesCountLine",
        "QuotientLine",
        "ThresholdGateLine",
        "AmountOrDividedByRateLine",
        "CountAtLeastLine",
        "CountAtMostLine",
        "YesOrNoCountLine",
        "CountNotRefusedLine",
        "MoreThanPerUnitLine",
        "CountWithoutRecordsLine",
        "AmountWhenMoreLine",
        "RatioTruncatedLine",
        "PositivePartOfNegationLine",
        "LesserOfWhenPositiveLine",
    ),
    "rate_tables": (
        "BracketColumnLine",
        "ContributionTierLine",
        "SurchargeTierLine",
        "TaperedAmountLine",
        "RateByIncomeBandLine",
        "ChosenRateAppliedLine",
        "AmountByCountLine",
    ),
    "choices": (
        "ChosenByCountLine",
        "ChosenByRangeLine",
        "ChosenBySignLine",
        "ConditionLine",
        "ConditionsCountLine",
    ),
    "record_lists": (
        "RecordTotalLine",
        "RecordCountLine",
        "FirstRecordCountLine",
        "RecordPositiveTotalLine",
        "ItemsTotalLine",
        "ItemSumLine",
        "ItemLesserOfLine",
    ),
    "forms": ("FormInstanceLine",),
}

HOMES: dict[str, dict[str, tuple[str, ...]]] = {
    CORE: CORE_HOMES,
}

PLACED = [
    (package, module, name)
    for package, modules in HOMES.items()
    for module, names in modules.items()
    for name in names
]
MODULES = [(package, module) for package, modules in HOMES.items() for module in modules]


@pytest.mark.parametrize("package", list(HOMES))
def test_trace_is_a_package(package: str) -> None:
    assert hasattr(importlib.import_module(package), "__path__")


@pytest.mark.parametrize(("package", "module", "name"), PLACED, ids=[name for *_, name in PLACED])
def test_each_class_lives_in_its_feature_module(package: str, module: str, name: str) -> None:
    home = importlib.import_module(f"{package}.{module}")

    assert getattr(home, name).__module__ == f"{package}.{module}"
    assert name in home.__all__


@pytest.mark.parametrize(("package", "module", "name"), PLACED, ids=[name for *_, name in PLACED])
def test_the_package_re_exports_each_class(package: str, module: str, name: str) -> None:
    home = importlib.import_module(f"{package}.{module}")

    assert getattr(importlib.import_module(package), name) is getattr(home, name)


@pytest.mark.parametrize(("package", "module"), MODULES, ids=[f"{p}.{m}" for p, m in MODULES])
def test_each_feature_module_exports_exactly_its_classes(package: str, module: str) -> None:
    home = importlib.import_module(f"{package}.{module}")

    assert set(home.__all__) == set(HOMES[package][module])


@pytest.mark.parametrize("package", list(HOMES))
def test_every_exported_line_class_is_placed(package: str) -> None:
    exported = {
        name
        for name, found in vars(importlib.import_module(package)).items()
        if inspect.isclass(found) and issubclass(found, TraceLine)
    }
    placed = {name for home, _, name in PLACED if home == package}

    assert exported - {"TraceLine"} == placed - {"TraceLine"}


@pytest.mark.parametrize("package", list(HOMES))
def test_the_package_exports_every_placed_name(package: str) -> None:
    placed = {name for home, _, name in PLACED if home == package}

    assert set(importlib.import_module(package).__all__) == placed


def test_core_exports_no_jurisdiction_line() -> None:
    moved = {
        name
        for package in (
            "tax_engine.jurisdictions.ca.trace",
            "tax_engine.jurisdictions.ca_on.trace",
        )
        for name in importlib.import_module(package).__all__
    }

    assert moved
    assert not moved & set(vars(tax_engine.domain.trace))
