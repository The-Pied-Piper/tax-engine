"""Unit tests for EnglishRendererRegistry, `@english_renderer` and EnglishTraceRenderer's lookup.

A line class's English text is a renderer class registered beside it (`line_class = <the line
class>`, `render(self, line) -> str`), keyed by the line class itself; EnglishTraceRenderer looks
the renderer up by `type(line)`, in the registry it is given or by default the shared one. Made-up
lines and renderers are never registered in the shared registry: the decorator tests point
`EnglishRendererRegistry.shared` at a fresh registry with monkeypatch, and the made-up package in
`rendering_fixtures` is imported only while it does, then forgotten.
"""

from __future__ import annotations

import importlib
import inspect
import sys
from collections.abc import Iterator
from dataclasses import dataclass
from decimal import Decimal
from types import ModuleType
from typing import assert_type

import pytest

# Imported first, so the core and jurisdiction renderers fill the real shared registry before any
# test points `shared` at a fresh one.
import tax_calculator.adapters.inbound.trace_english
import tax_calculator.domain.trace
import tax_calculator.jurisdictions.ca.trace
import tax_calculator.jurisdictions.ca_on.trace
from tax_calculator.adapters.inbound.trace_english import EnglishTraceRenderer
from tax_calculator.adapters.inbound.trace_english.registry import (
    EnglishRendererRegistry,
    english_renderer,
)
from tax_calculator.adapters.outbound.parameter_parsers.registry import ParameterParserRegistry
from tax_calculator.domain.artifact import ArtifactKind
from tax_calculator.domain.errors import DuplicateRegistrationError, UnknownRegistrationError
from tax_calculator.domain.registry import Registry
from tax_calculator.domain.trace import SumLine, TraceLine

D = Decimal

EX_TOTAL = ArtifactKind("ex/total", Decimal)

REAL_SHARED = EnglishRendererRegistry.shared()  # before any test points `shared` elsewhere


@dataclass(frozen=True)
class ExampleLine(TraceLine):
    """A made-up line class, registered only in registries the tests create."""

    figure: Decimal

    @property
    def amount(self) -> Decimal:
        return self.figure


@dataclass(frozen=True)
class ExampleSubLine(ExampleLine):
    """A subclass of the made-up line class, with no renderer of its own."""


class ExampleRenderer:
    """The made-up line's English text."""

    line_class = ExampleLine

    def render(self, line: ExampleLine) -> str:
        return f"example of {line.figure}"


class OtherExampleRenderer(ExampleRenderer):
    """A second renderer for the same made-up line class."""


@pytest.fixture
def fresh(monkeypatch: pytest.MonkeyPatch) -> EnglishRendererRegistry:
    """A fresh registry that `@english_renderer` registers into for the duration of one test."""
    registry = EnglishRendererRegistry()
    monkeypatch.setattr(EnglishRendererRegistry, "shared", classmethod(lambda cls: registry))
    return registry


# --- registration and lookup by line class -----------------------------------------------------


def test_english_renderer_registry_is_a_registry() -> None:
    assert issubclass(EnglishRendererRegistry, Registry)


def test_register_class_returns_the_class_unchanged() -> None:
    registered = EnglishRendererRegistry().register_class(ExampleRenderer)

    assert_type(registered, type[ExampleRenderer])

    assert registered is ExampleRenderer


def test_for_line_class_returns_the_renderer_registered_for_the_class() -> None:
    registry = EnglishRendererRegistry()
    registry.register_class(ExampleRenderer)

    found = registry.for_line_class(ExampleLine)

    assert isinstance(found, ExampleRenderer)
    assert found.line_class is ExampleLine
    assert found.render(ExampleLine(D("2.5"))) == "example of 2.5"


def test_registering_two_renderers_for_one_line_class_fails() -> None:
    registry = EnglishRendererRegistry()
    registry.register_class(ExampleRenderer)
    first = registry.for_line_class(ExampleLine)

    with pytest.raises(DuplicateRegistrationError, match="ExampleLine"):
        registry.register_class(OtherExampleRenderer)

    assert registry.for_line_class(ExampleLine) is first  # never silently overridden


def test_looking_up_a_line_class_without_a_renderer_fails_naming_it() -> None:
    registry = EnglishRendererRegistry()

    with pytest.raises(UnknownRegistrationError, match="ExampleLine"):
        registry.for_line_class(ExampleLine)


def test_a_subclass_of_a_registered_line_class_has_no_renderer() -> None:
    # Keyed by the exact class, as EnglishTraceRenderer looks up `type(line)`.
    registry = EnglishRendererRegistry()
    registry.register_class(ExampleRenderer)

    with pytest.raises(UnknownRegistrationError, match="ExampleSubLine"):
        registry.for_line_class(ExampleSubLine)


def test_a_non_renderer_stored_under_a_line_class_key_is_unknown() -> None:
    # The inherited string-keyed `register` bypasses `register_class`; `for_line_class` must not
    # trust what it finds there.
    registry = EnglishRendererRegistry()
    registry.register(f"{ExampleLine.__module__}.{ExampleLine.__qualname__}", 42)

    with pytest.raises(UnknownRegistrationError, match="ExampleLine"):
        registry.for_line_class(ExampleLine)


# --- the shared registry ---------------------------------------------------------------------


def test_shared_returns_the_same_instance_every_time() -> None:
    assert EnglishRendererRegistry.shared() is EnglishRendererRegistry.shared()
    assert isinstance(EnglishRendererRegistry.shared(), EnglishRendererRegistry)


def test_a_directly_constructed_registry_is_separate_and_empty() -> None:
    registry = EnglishRendererRegistry()

    assert registry is not EnglishRendererRegistry.shared()
    with pytest.raises(UnknownRegistrationError):
        registry.for_line_class(SumLine)


def test_shared_renderer_registry_is_not_the_shared_parser_registry() -> None:
    assert id(EnglishRendererRegistry.shared()) != id(ParameterParserRegistry.shared())


def test_the_shared_registry_holds_exactly_the_built_in_renderers() -> None:
    assert REAL_SHARED.identifiers() == {
        "tax_calculator.domain.trace.arithmetic.AmountOrDividedByRateLine",
        "tax_calculator.domain.trace.arithmetic.AmountWhenMoreLine",
        "tax_calculator.domain.trace.arithmetic.AtMostLine",
        "tax_calculator.domain.trace.arithmetic.CappedAmountLine",
        "tax_calculator.domain.trace.arithmetic.ClaimAtMostLine",
        "tax_calculator.domain.trace.arithmetic.CountAtLeastLine",
        "tax_calculator.domain.trace.arithmetic.CountAtMostLine",
        "tax_calculator.domain.trace.arithmetic.CountNotRefusedLine",
        "tax_calculator.domain.trace.arithmetic.CountWithoutRecordsLine",
        "tax_calculator.domain.trace.arithmetic.CreditAmountLine",
        "tax_calculator.domain.trace.arithmetic.DividedByRateLine",
        "tax_calculator.domain.trace.arithmetic.FractionAppliedLine",
        "tax_calculator.domain.trace.arithmetic.GreaterOfLine",
        "tax_calculator.domain.trace.arithmetic.LesserOfLine",
        "tax_calculator.domain.trace.arithmetic.LesserOfWhenPositiveLine",
        "tax_calculator.domain.trace.arithmetic.LesserOfWithMaximumLine",
        "tax_calculator.domain.trace.arithmetic.MoreThanPerUnitLine",
        "tax_calculator.domain.trace.arithmetic.MultipleOverLine",
        "tax_calculator.domain.trace.arithmetic.PerUnitAmountLine",
        "tax_calculator.domain.trace.arithmetic.PositivePartOfNegationLine",
        "tax_calculator.domain.trace.arithmetic.QuotientLine",
        "tax_calculator.domain.trace.arithmetic.RateAppliedLine",
        "tax_calculator.domain.trace.arithmetic.RatioAppliedLine",
        "tax_calculator.domain.trace.arithmetic.RatioTruncatedLine",
        "tax_calculator.domain.trace.arithmetic.RoundedTotalLine",
        "tax_calculator.domain.trace.arithmetic.SignChosenDifferenceLine",
        "tax_calculator.domain.trace.arithmetic.SubtractedLine",
        "tax_calculator.domain.trace.arithmetic.SubtractedNotBelowZeroLine",
        "tax_calculator.domain.trace.arithmetic.SumLine",
        "tax_calculator.domain.trace.arithmetic.SumNotBelowZeroLine",
        "tax_calculator.domain.trace.arithmetic.ThresholdGateLine",
        "tax_calculator.domain.trace.arithmetic.TimesCountLine",
        "tax_calculator.domain.trace.arithmetic.YesOrNoCountLine",
        "tax_calculator.domain.trace.choices.ChosenByCountLine",
        "tax_calculator.domain.trace.choices.ChosenByRangeLine",
        "tax_calculator.domain.trace.choices.ChosenBySignLine",
        "tax_calculator.domain.trace.choices.ConditionLine",
        "tax_calculator.domain.trace.choices.ConditionsCountLine",
        "tax_calculator.domain.trace.forms.FormInstanceLine",
        "tax_calculator.domain.trace.rate_tables.AmountByCountLine",
        "tax_calculator.domain.trace.rate_tables.BracketColumnLine",
        "tax_calculator.domain.trace.rate_tables.ChosenRateAppliedLine",
        "tax_calculator.domain.trace.rate_tables.ContributionTierLine",
        "tax_calculator.domain.trace.rate_tables.RateByIncomeBandLine",
        "tax_calculator.domain.trace.rate_tables.SurchargeTierLine",
        "tax_calculator.domain.trace.rate_tables.TaperedAmountLine",
        "tax_calculator.domain.trace.record_lists.FirstRecordCountLine",
        "tax_calculator.domain.trace.record_lists.ItemLesserOfLine",
        "tax_calculator.domain.trace.record_lists.ItemSumLine",
        "tax_calculator.domain.trace.record_lists.ItemsTotalLine",
        "tax_calculator.domain.trace.record_lists.RecordCountLine",
        "tax_calculator.domain.trace.record_lists.RecordPositiveTotalLine",
        "tax_calculator.domain.trace.record_lists.RecordTotalLine",
        "tax_calculator.jurisdictions.ca.trace.apprenticeship.ApprenticeWagesLine",
        "tax_calculator.jurisdictions.ca.trace.capital_cost.CcaClaimLine",
        "tax_calculator.jurisdictions.ca.trace.capital_cost.CcaVehicleProceedsLine",
        "tax_calculator.jurisdictions.ca.trace.capital_cost.CcaZepvProceedsLine",
        "tax_calculator.jurisdictions.ca.trace.capital_cost.CcaPartACheckLine",
        "tax_calculator.jurisdictions.ca.trace.capital_cost.CcaChangeInUseCheckLine",
        "tax_calculator.jurisdictions.ca.trace.capital_cost.CcaPartBCheckLine",
        "tax_calculator.jurisdictions.ca.trace.capital_cost.CcaVehicleAdditionsCheckLine",
        "tax_calculator.jurisdictions.ca.trace.capital_cost.CcaVehicleClassCheckLine",
        "tax_calculator.jurisdictions.ca.trace.capital_cost.CcaVehicleNonArmsLengthCheckLine",
        "tax_calculator.jurisdictions.ca.trace.capital_cost.CcaVehicleChangeInUseCheckLine",
        "tax_calculator.jurisdictions.ca.trace.capital_cost.ClosingUccLine",
        "tax_calculator.jurisdictions.ca.trace.capital_cost.FiscalPeriodDaysFromDatesLine",
        "tax_calculator.jurisdictions.ca.trace.capital_cost.FiscalPeriodDaysLine",
        "tax_calculator.jurisdictions.ca.trace.capital_cost.ImmediateExpensingLine",
        "tax_calculator.jurisdictions.ca.trace.capital_cost.ProratedByDaysLine",
        "tax_calculator.jurisdictions.ca.trace.capital_cost.ProratedByDaysInPeriodLine",
        "tax_calculator.jurisdictions.ca.trace.capital_cost.ImmediateExpensingAgreedLimitLine",
        "tax_calculator.jurisdictions.ca.trace.capital_cost.RecapturedCcaLine",
        "tax_calculator.jurisdictions.ca.trace.capital_cost.TerminalLossLine",
        "tax_calculator.jurisdictions.ca.trace.vehicles.BusinessVehicleLine",
        "tax_calculator.jurisdictions.ca.trace.vehicles.YearAmountLine",
        "tax_calculator.jurisdictions.ca.trace.dependants.CaregiverClaimLine",
        "tax_calculator.jurisdictions.ca.trace.dependants.DisabilityTransferLine",
        "tax_calculator.jurisdictions.ca.trace.dependants.OtherDependantMedicalLine",
        "tax_calculator.jurisdictions.ca.trace.logging_tax_credit.LoggingTaxCreditLine",
        "tax_calculator.jurisdictions.ca.trace.farm_chart.PercentageOfLine",
        "tax_calculator.jurisdictions.ca.trace.foreign_tax.ForeignBusinessLine10",
        "tax_calculator.jurisdictions.ca.trace.foreign_tax.ForeignBusinessLine11",
        "tax_calculator.jurisdictions.ca.trace.foreign_tax.ForeignBusinessLine4",
        "tax_calculator.jurisdictions.ca.trace.foreign_tax.ForeignBusinessLine5",
        "tax_calculator.jurisdictions.ca.trace.foreign_tax.ForeignBusinessLine7",
        "tax_calculator.jurisdictions.ca.trace.foreign_tax.ForeignBusinessLine8",
        "tax_calculator.jurisdictions.ca.trace.foreign_tax.ForeignPropertyTaxLine",
        "tax_calculator.jurisdictions.ca.trace.foreign_tax.ForeignTaxCreditLine",
        "tax_calculator.jurisdictions.ca.trace.foreign_tax.PooledForeignTaxCreditLine",
        "tax_calculator.jurisdictions.ca.trace.home_renovation.RenovationLine3",
        "tax_calculator.jurisdictions.ca.trace.home_renovation.RenovationLine6",
        "tax_calculator.jurisdictions.ca.trace.home_renovation.RenovationLine7",
        "tax_calculator.jurisdictions.ca.trace.gains.DispositionGainLine",
        "tax_calculator.jurisdictions.ca.trace.gains.DispositionGainOnlyLine",
        "tax_calculator.jurisdictions.ca.trace.gains.DepreciablePropertyGainLine",
        "tax_calculator.jurisdictions.ca.trace.gains.QffpGainLine",
        "tax_calculator.jurisdictions.ca.trace.gains.FarmLossAppliedLine",
        "tax_calculator.jurisdictions.ca.trace.gains.PersonalUsePropertyGainLine",
        "tax_calculator.jurisdictions.ca.trace.gains.DispositionProceedsLine",
        "tax_calculator.jurisdictions.ca.trace.gains.NetCapitalLossesRowLine",
        "tax_calculator.jurisdictions.ca.trace.gains.PrincipalResidenceDesignationBox",
        "tax_calculator.jurisdictions.ca.trace.gains.PrincipalResidenceGainLine",
        "tax_calculator.jurisdictions.ca.trace.gains.PrincipalResidenceLine27",
        "tax_calculator.jurisdictions.ca.trace.gains.PrincipalResidenceLine29",
        "tax_calculator.jurisdictions.ca.trace.gains.PrincipalResidenceLine30",
        "tax_calculator.jurisdictions.ca.trace.gains.PrincipalResidenceLine32",
        "tax_calculator.jurisdictions.ca.trace.gains.PrincipalResidenceLine33",
        "tax_calculator.jurisdictions.ca.trace.gains.PrincipalResidenceLine38",
        "tax_calculator.jurisdictions.ca.trace.gains.PrincipalResidenceLine39",
        "tax_calculator.jurisdictions.ca.trace.gains.PrincipalResidenceLine42",
        "tax_calculator.jurisdictions.ca.trace.gains.PrincipalResidenceLine44",
        "tax_calculator.jurisdictions.ca.trace.gains.PrincipalResidenceLine45",
        "tax_calculator.jurisdictions.ca.trace.gains.PrincipalResidenceLine48",
        "tax_calculator.jurisdictions.ca.trace.gains.PrincipalResidenceLine51",
        "tax_calculator.jurisdictions.ca.trace.gains.PrincipalResidenceLine53",
        "tax_calculator.jurisdictions.ca.trace.gains.PrincipalResidenceWorksheetLine3",
        "tax_calculator.jurisdictions.ca.trace.gains.PrincipalResidenceWorksheetLine6",
        "tax_calculator.jurisdictions.ca.trace.gains.PrincipalResidenceWorksheetLine16",
        "tax_calculator.jurisdictions.ca.trace.gains.PrincipalResidenceWorksheetLine17",
        "tax_calculator.jurisdictions.ca.trace.gains.PrincipalResidenceWorksheetLine18",
        "tax_calculator.jurisdictions.ca.trace.gains.PrincipalResidenceWorksheetLine19",
        "tax_calculator.jurisdictions.ca.trace.gains.PrincipalResidenceWorksheetLine21",
        "tax_calculator.jurisdictions.ca.trace.gains.PrincipalResidenceWorksheetLine23",
        "tax_calculator.jurisdictions.ca.trace.gains.PrincipalResidenceWorksheetLine24",
        "tax_calculator.jurisdictions.ca.trace.gains.PrincipalResidenceWorksheetLine26",
        "tax_calculator.jurisdictions.ca.trace.gains.PrincipalResidenceWorksheetLine27",
        "tax_calculator.jurisdictions.ca.trace.gains.PrincipalResidenceWorksheetLine30",
        "tax_calculator.jurisdictions.ca.trace.gains.PrincipalResidenceWorksheetLine32",
        "tax_calculator.jurisdictions.ca.trace.gains.PrincipalResidenceWorksheetLine33",
        "tax_calculator.jurisdictions.ca.trace.gains.PrincipalResidenceWorksheetLine35",
        "tax_calculator.jurisdictions.ca.trace.gains.PrincipalResidenceWorksheetLine36",
        "tax_calculator.jurisdictions.ca.trace.gains.PrincipalResidenceWorksheetLine40",
        "tax_calculator.jurisdictions.ca.trace.gains.PrincipalResidenceWorksheetLine41",
        "tax_calculator.jurisdictions.ca.trace.gains.PrincipalResidenceWorksheetLine44",
        "tax_calculator.jurisdictions.ca.trace.gains.PrincipalResidenceWorksheetLine46",
        "tax_calculator.jurisdictions.ca.trace.gains.PrincipalResidenceWorksheetLine47",
        "tax_calculator.jurisdictions.ca.trace.gains.PrincipalResidenceWorksheetLine50",
        "tax_calculator.jurisdictions.ca.trace.gains.PrincipalResidenceWorksheetLine53",
        "tax_calculator.jurisdictions.ca.trace.gains.PrincipalResidenceWorksheetLine55",
        "tax_calculator.jurisdictions.ca.trace.gains.PrincipalResidenceWorksheetLine58",
        "tax_calculator.jurisdictions.ca.trace.gains.PrincipalResidenceWorksheetLine59",
        "tax_calculator.jurisdictions.ca.trace.gains.PrincipalResidenceWorksheetLine61",
        "tax_calculator.jurisdictions.ca.trace.gains.PrincipalResidenceWorksheetLine63",
        "tax_calculator.jurisdictions.ca.trace.gains.PrincipalResidenceWorksheetLine64",
        "tax_calculator.jurisdictions.ca.trace.gains.PrincipalResidenceWorksheetLine66",
        "tax_calculator.jurisdictions.ca.trace.gains.PrincipalResidenceLine56",
        "tax_calculator.jurisdictions.ca.trace.gains.PrincipalResidenceLine57",
        "tax_calculator.jurisdictions.ca.trace.gains.ReserveRowForPeriodLine",
        "tax_calculator.jurisdictions.ca.trace.gains.QbtBeforeQccLine",
        "tax_calculator.domain.trace.arithmetic.PercentageAppliedLine",
        "tax_calculator.jurisdictions.ca.trace.rentals.RentalAdditionLine",
        "tax_calculator.jurisdictions.ca.trace.rentals.ShortTermRentalNonCompliantCcaByClassLine",
        "tax_calculator.jurisdictions.ca.trace.rentals.ShortTermRentalNonCompliantCcaLine",
        "tax_calculator.jurisdictions.ca.trace.rentals.ShortTermRentalNonCompliantLine",
        "tax_calculator.jurisdictions.ca_on.trace.capped_records.CappedRecordLine",
        "tax_calculator.jurisdictions.ca_on.trace.dependants.CaregiverClaimLessClaimedLine",
        "tax_calculator.jurisdictions.ca_on.trace.foreign_tax.ProvincialForeignTaxCreditLine",
        "tax_calculator.jurisdictions.ca_on.trace.foreign_tax.PooledProvincialForeignTaxCreditLine",
        "tax_calculator.jurisdictions.ca_on.trace.placement_credit.PlacementCreditLine",
    }


# --- the decorator ---------------------------------------------------------------------------


def test_decorator_registers_an_instance_under_its_line_class(
    fresh: EnglishRendererRegistry,
) -> None:
    english_renderer(ExampleRenderer)

    assert isinstance(fresh.for_line_class(ExampleLine), ExampleRenderer)


def test_decorator_returns_the_class_unchanged(fresh: EnglishRendererRegistry) -> None:
    decorated = english_renderer(ExampleRenderer)

    assert_type(decorated, type[ExampleRenderer])

    assert decorated is ExampleRenderer


def test_decorating_a_second_renderer_for_one_line_class_fails(
    fresh: EnglishRendererRegistry,
) -> None:
    english_renderer(ExampleRenderer)

    with pytest.raises(DuplicateRegistrationError, match="ExampleLine"):
        english_renderer(OtherExampleRenderer)


# --- EnglishTraceRenderer looks renderers up -------------------------------------------------


def test_the_renderer_renders_a_line_with_the_renderer_registered_for_its_class() -> None:
    registry = EnglishRendererRegistry()
    registry.register_class(ExampleRenderer)

    renderer = EnglishTraceRenderer(registry)

    assert renderer.render(ExampleLine(D("3.50"))) == "example of 3.50"
    assert renderer.render_all((ExampleLine(D(1)), ExampleLine(D(2)))) == (
        "example of 1",
        "example of 2",
    )


def test_an_unregistered_line_class_fails_naming_it_and_the_language() -> None:
    renderer = EnglishTraceRenderer(EnglishRendererRegistry())

    with pytest.raises(TypeError, match=r"^no English rendering for trace line ExampleLine$"):
        renderer.render(ExampleLine(D(1)))


def test_a_renderer_given_a_private_registry_does_not_use_the_shared_one() -> None:
    renderer = EnglishTraceRenderer(EnglishRendererRegistry())

    with pytest.raises(TypeError, match=r"^no English rendering for trace line SumLine$"):
        renderer.render(SumLine(EX_TOTAL, (), D(1)))


def test_a_renderer_registered_in_a_private_registry_is_unknown_to_the_default_renderer() -> None:
    EnglishRendererRegistry().register_class(ExampleRenderer)

    with pytest.raises(TypeError, match=r"^no English rendering for trace line ExampleLine$"):
        EnglishTraceRenderer().render(ExampleLine(D(1)))


def test_the_default_renderer_uses_the_shared_registry(fresh: EnglishRendererRegistry) -> None:
    english_renderer(ExampleRenderer)

    assert EnglishTraceRenderer().render(ExampleLine(D(4))) == "example of 4"


# --- every core and jurisdiction line class has English text; core's sits beside its module ----

# The core and jurisdiction trace packages, imported above so that all their renderers are
# registered; where each jurisdiction's renderers live is checked under tests/jurisdictions.
TRACE_PACKAGES: tuple[ModuleType, ...] = (
    tax_calculator.domain.trace,
    tax_calculator.jurisdictions.ca.trace,
    tax_calculator.jurisdictions.ca_on.trace,
)


def exported_line_classes() -> list[type[TraceLine]]:
    """Every TraceLine subclass the core and jurisdiction trace packages export, by name."""
    return sorted(
        {
            found
            for package in TRACE_PACKAGES
            for found in vars(package).values()
            if inspect.isclass(found) and issubclass(found, TraceLine) and found is not TraceLine
        },
        key=lambda cls: cls.__name__,
    )


@pytest.mark.parametrize("line_class", exported_line_classes(), ids=lambda cls: cls.__name__)
def test_every_exported_line_class_has_a_shared_english_renderer(
    line_class: type[TraceLine],
) -> None:
    found = EnglishRendererRegistry.shared().for_line_class(line_class)

    assert getattr(found, "line_class") is line_class  # noqa: B009
    assert callable(getattr(found, "render", None))


def core_line_classes() -> list[type[TraceLine]]:
    """Every TraceLine subclass the core trace package exports, by name."""
    return [
        cls
        for cls in exported_line_classes()
        if cls.__module__.startswith("tax_calculator.domain.trace.")
    ]


@pytest.mark.parametrize("line_class", core_line_classes(), ids=lambda cls: cls.__name__)
def test_each_core_renderer_lives_in_the_adapter_module_matching_its_line_classs_module(
    line_class: type[TraceLine],
) -> None:
    # SumLine in tax_calculator.domain.trace.arithmetic -> its renderer in trace_english.arithmetic.
    feature = line_class.__module__.rsplit(".", 1)[1]
    found = EnglishRendererRegistry.shared().for_line_class(line_class)

    assert type(found).__module__ == f"tax_calculator.adapters.inbound.trace_english.{feature}"


def test_the_adapter_is_a_package_with_registry_and_renderer_modules() -> None:
    assert hasattr(tax_calculator.adapters.inbound.trace_english, "__path__")
    assert (
        EnglishRendererRegistry.__module__
        == "tax_calculator.adapters.inbound.trace_english.registry"
    )
    assert english_renderer.__module__ == "tax_calculator.adapters.inbound.trace_english.registry"
    assert (
        EnglishTraceRenderer.__module__ == "tax_calculator.adapters.inbound.trace_english.renderer"
    )


# --- a made-up package adds a line class and its English text --------------------------------

LEVIES = "tests.adapters.inbound.rendering_fixtures.levies"


@pytest.fixture
def levies(fresh: EnglishRendererRegistry) -> Iterator[ModuleType]:
    """The made-up package's module, imported (so registered) into the fresh registry only.

    Forgotten afterwards, so the next test importing it registers it again into its own registry
    and the shared registry never holds it.
    """
    sys.modules.pop(LEVIES, None)
    yield importlib.import_module(LEVIES)
    sys.modules.pop(LEVIES, None)


def test_a_made_up_packages_line_is_rendered_with_its_own_text(
    levies: ModuleType, fresh: EnglishRendererRegistry
) -> None:
    line = levies.ExLevyLine(ArtifactKind("ex/levy", Decimal), D("12.5"))

    assert EnglishTraceRenderer(fresh).render(line) == "levy: levy of 12.5"


def test_importing_the_made_up_package_registers_its_renderer(
    levies: ModuleType, fresh: EnglishRendererRegistry
) -> None:
    found = fresh.for_line_class(levies.ExLevyLine)

    assert isinstance(found, levies.ExLevyRenderer)


def test_the_made_up_line_is_not_in_the_real_shared_registry(levies: ModuleType) -> None:
    # `fresh` stands in for `shared` here; the real shared registry was kept at import.
    with pytest.raises(UnknownRegistrationError, match="ExLevyLine"):
        REAL_SHARED.for_line_class(levies.ExLevyLine)
