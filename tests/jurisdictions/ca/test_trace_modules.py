"""Unit tests for the layout of the federal Canada trace package: each line class's home module.

The federal Canada line classes live in `tax_calculator.jurisdictions.ca.trace`, one module per
feature
group, each with an `__all__`; its `__init__` re-exports every module's `__all__`. Every exported
line class appears in `HOMES`, so a new one is placed deliberately. Each has a renderer in the
matching module of `tax_calculator.jurisdictions.ca.trace_english`.
"""

from __future__ import annotations

import importlib
import inspect

import pytest

import tax_calculator.jurisdictions.ca.trace_english  # noqa: F401  (registers the renderers)
from tax_calculator.adapters.inbound.trace_english.registry import EnglishRendererRegistry
from tax_calculator.domain.trace import TraceLine

PACKAGE = "tax_calculator.jurisdictions.ca.trace"
RENDERERS = "tax_calculator.jurisdictions.ca.trace_english"

HOMES: dict[str, tuple[str, ...]] = {
    "capital_cost": (
        "CcaZeroReason",
        "CcaClaimLine",
        "RecapturedCcaLine",
        "TerminalLossLine",
        "CcaVehicleProceedsLine",
        "CcaZepvProceedsLine",
        "CcaPartACheckLine",
        "CcaChangeInUseCheckLine",
        "CcaPartBCheckLine",
        "CcaVehicleAdditionsCheckLine",
        "CcaVehicleClassCheckLine",
        "CcaVehicleNonArmsLengthCheckLine",
        "CcaVehicleChangeInUseCheckLine",
        "ClosingUccLine",
        "FiscalPeriodDaysFromDatesLine",
        "FiscalPeriodDaysLine",
        "ProratedByDaysLine",
        "ProratedByDaysInPeriodLine",
        "ImmediateExpensingLine",
        "ImmediateExpensingAgreedLimitLine",
    ),
    "apprenticeship": ("ApprenticeWagesLine",),
    "home_renovation": ("RenovationLine3", "RenovationLine6", "RenovationLine7"),
    "vehicles": ("BusinessVehicleLine", "YearAmountLine"),
    "dependants": (
        "CaregiverClaimLine",
        "OtherDependantMedicalLine",
        "DisabilityTransferLine",
    ),
    "logging_tax_credit": ("LoggingTaxCreditLine",),
    "farm_chart": ("PercentageOfLine",),
    "foreign_tax": (
        "ForeignPropertyTaxLine",
        "ForeignTaxCreditLine",
        "PooledForeignTaxCreditLine",
        "ForeignBusinessLine4",
        "ForeignBusinessLine5",
        "ForeignBusinessLine7",
        "ForeignBusinessLine8",
        "ForeignBusinessLine10",
        "ForeignBusinessLine11",
    ),
    "gains": (
        "PrincipalResidenceDesignationBox",
        "PrincipalResidenceGainLine",
        "PrincipalResidenceLine27",
        "PrincipalResidenceLine29",
        "PrincipalResidenceLine30",
        "PrincipalResidenceLine32",
        "PrincipalResidenceLine33",
        "PrincipalResidenceLine38",
        "PrincipalResidenceLine39",
        "PrincipalResidenceLine42",
        "PrincipalResidenceLine44",
        "PrincipalResidenceLine45",
        "PrincipalResidenceLine48",
        "PrincipalResidenceLine51",
        "PrincipalResidenceLine53",
        "PrincipalResidenceWorksheetLine3",
        "PrincipalResidenceWorksheetLine6",
        "PrincipalResidenceWorksheetLine16",
        "PrincipalResidenceWorksheetLine17",
        "PrincipalResidenceWorksheetLine18",
        "PrincipalResidenceWorksheetLine19",
        "PrincipalResidenceWorksheetLine21",
        "PrincipalResidenceWorksheetLine23",
        "PrincipalResidenceWorksheetLine24",
        "PrincipalResidenceWorksheetLine26",
        "PrincipalResidenceWorksheetLine27",
        "PrincipalResidenceWorksheetLine30",
        "PrincipalResidenceWorksheetLine32",
        "PrincipalResidenceWorksheetLine33",
        "PrincipalResidenceWorksheetLine35",
        "PrincipalResidenceWorksheetLine36",
        "PrincipalResidenceWorksheetLine40",
        "PrincipalResidenceWorksheetLine41",
        "PrincipalResidenceWorksheetLine44",
        "PrincipalResidenceWorksheetLine46",
        "PrincipalResidenceWorksheetLine47",
        "PrincipalResidenceWorksheetLine50",
        "PrincipalResidenceWorksheetLine53",
        "PrincipalResidenceWorksheetLine55",
        "PrincipalResidenceWorksheetLine58",
        "PrincipalResidenceWorksheetLine59",
        "PrincipalResidenceWorksheetLine61",
        "PrincipalResidenceWorksheetLine63",
        "PrincipalResidenceWorksheetLine64",
        "PrincipalResidenceWorksheetLine66",
        "PrincipalResidenceLine56",
        "PrincipalResidenceLine57",
        "DispositionGainLine",
        "DispositionGainOnlyLine",
        "DepreciablePropertyGainLine",
        "QffpGainLine",
        "FarmLossAppliedLine",
        "PersonalUsePropertyGainLine",
        "DispositionProceedsLine",
        "NetCapitalLossesRowLine",
        "ReserveRowForPeriodLine",
        "QbtBeforeQccLine",
    ),
    "rentals": (
        "RentalAdditionLine",
        "ShortTermRentalNonCompliantLine",
        "ShortTermRentalNonCompliantCcaLine",
        "ShortTermRentalNonCompliantCcaByClassLine",
    ),
}

PLACED = [(module, name) for module, names in HOMES.items() for name in names]


def test_trace_is_a_package() -> None:
    assert hasattr(importlib.import_module(PACKAGE), "__path__")


@pytest.mark.parametrize(("module", "name"), PLACED, ids=[name for _, name in PLACED])
def test_each_class_lives_in_its_feature_module(module: str, name: str) -> None:
    home = importlib.import_module(f"{PACKAGE}.{module}")

    assert getattr(home, name).__module__ == f"{PACKAGE}.{module}"
    assert name in home.__all__


@pytest.mark.parametrize(("module", "name"), PLACED, ids=[name for _, name in PLACED])
def test_the_package_re_exports_each_class(module: str, name: str) -> None:
    home = importlib.import_module(f"{PACKAGE}.{module}")

    assert getattr(importlib.import_module(PACKAGE), name) is getattr(home, name)


@pytest.mark.parametrize("module", list(HOMES))
def test_each_feature_module_exports_exactly_its_classes(module: str) -> None:
    home = importlib.import_module(f"{PACKAGE}.{module}")

    assert set(home.__all__) == set(HOMES[module])


def test_every_exported_line_class_is_placed() -> None:
    exported = {
        name
        for name, found in vars(importlib.import_module(PACKAGE)).items()
        if inspect.isclass(found) and issubclass(found, TraceLine)
    }
    # The package exports only its own lines; CcaZeroReason is not a line class.
    placed = {name for _, name in PLACED if name != "CcaZeroReason"}

    assert exported - {"TraceLine"} == placed - {"TraceLine"}


def test_the_package_exports_every_placed_name() -> None:
    placed = {name for _, name in PLACED}

    assert set(importlib.import_module(PACKAGE).__all__) == placed


def _line_classes() -> list[type[TraceLine]]:
    homes = [(importlib.import_module(f"{PACKAGE}.{module}"), name) for module, name in PLACED]
    found = [getattr(home, name) for home, name in homes]
    return [cls for cls in found if inspect.isclass(cls) and issubclass(cls, TraceLine)]


@pytest.mark.parametrize("line_class", _line_classes(), ids=lambda cls: cls.__name__)
def test_every_line_class_has_a_shared_english_renderer(line_class: type[TraceLine]) -> None:
    found = EnglishRendererRegistry.shared().for_line_class(line_class)

    assert getattr(found, "line_class") is line_class  # noqa: B009
    assert callable(getattr(found, "render", None))


@pytest.mark.parametrize("line_class", _line_classes(), ids=lambda cls: cls.__name__)
def test_each_renderer_lives_in_the_adapter_module_matching_its_line_classs_module(
    line_class: type[TraceLine],
) -> None:
    feature = line_class.__module__.rsplit(".", 1)[1]
    found = EnglishRendererRegistry.shared().for_line_class(line_class)

    assert type(found).__module__ == f"{RENDERERS}.{feature}"
