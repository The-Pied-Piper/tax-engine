"""Every resolvable tax year of every listed jurisdiction composes.

Year resolution takes the greatest `valid_from_tax_year` at or below the year asked, so a manifest
valid from 2025 also serves 2026; a dataset added for one year only, or missing for a later one,
fails that later return and nothing else builds it. The tax years to test for a jurisdiction are
every year from its earliest manifest's `valid_from_tax_year` up to the greatest year any dataset
file `<root>/parameters/**/<YYYY>.yaml` names. No figures: only that each year composes. Names in
the unit tests are made up: the packages `ex`, `ex-on` and `ex-ab`.
"""

from __future__ import annotations

import re
from collections.abc import Iterable, Mapping
from pathlib import Path

import pytest

from tax_engine import factory
from tax_engine.adapters.outbound.yaml_jurisdictions import YamlJurisdictionSource
from tax_engine.adapters.outbound.yaml_parameters import YamlParameterSource
from tax_engine.application.services.tax_computation import TaxComputationService
from tax_engine.domain.capability import CapabilityRegistry
from tax_engine.domain.errors import DomainError
from tax_engine.domain.jurisdiction import Jurisdiction
from tax_engine.domain.jurisdiction_code import JurisdictionCode
from tax_engine.domain.registry import Namespace
from tax_engine.jurisdictions.core.capabilities.credit_amount import CreditAmount
from tax_engine.registrations import JURISDICTIONS, artifact_kinds, parameter_parsers, units
from tests.adapters.outbound.test_yaml_import_rebinds import province, write_benefit
from tests.adapters.outbound.test_yaml_imports import EX_ON, Half, package_roots, source
from tests.adapters.outbound.test_yaml_jurisdictions import write

YEAR_FILE = re.compile(r"\d{4}\.yaml")


def dataset_years(roots: Iterable[Path]) -> set[int]:
    """The years named by the files `<root>/parameters/**/<YYYY>.yaml` under `roots`."""
    return {
        int(path.stem)
        for root in roots
        for path in (root / "parameters").rglob("*.yaml")
        if YEAR_FILE.fullmatch(path.name)
    }


def resolvable_years(roots: Iterable[Path], jurisdiction: Jurisdiction) -> list[int]:
    """Each year from the earliest manifest's start to the greatest dataset or manifest start year."""
    starts = [manifest.valid_from_tax_year for manifest in jurisdiction.manifests]
    first = min(starts)
    last = max([*dataset_years(roots), *starts])
    return list(range(first, last + 1))


def composition_failures(
    service: TaxComputationService, code: JurisdictionCode, years: Iterable[int]
) -> list[str]:
    """One line for each year of `code` that does not compose, naming code, year and the error."""
    failures: list[str] = []
    for year in years:
        try:
            service.compose(code, year)
        except DomainError as exc:
            failures.append(f"{code}, tax year {year}: {exc}")
    return failures


def require_every_year_composes(
    service: TaxComputationService, code: JurisdictionCode, years: Iterable[int]
) -> None:
    """Fail, listing every failing year, if any of `years` does not compose for `code`."""
    failures = composition_failures(service, code, years)
    if failures:
        pytest.fail("\n".join(failures), pytrace=False)


# --- the real jurisdictions -------------------------------------------------------------------


@pytest.mark.parametrize("code", JURISDICTIONS.jurisdiction_codes(), ids=str)
def test_every_resolvable_tax_year_of_a_listed_jurisdiction_composes(
    code: JurisdictionCode,
) -> None:
    roots = JURISDICTIONS.roots()
    service = factory.build_tax_computation()
    jurisdiction = YamlJurisdictionSource(roots, artifact_kinds(), units()).get_jurisdiction(code)

    require_every_year_composes(service, code, resolvable_years(roots.values(), jurisdiction))


def test_the_listed_jurisdictions_are_not_empty() -> None:
    assert JurisdictionCode("CA-ON") in JURISDICTIONS.jurisdiction_codes()


# --- the guard itself, on made-up packages ---------------------------------------------------

SECOND_STEP = (
    "  - name: core/credit_amount\n"
    "    params: {amount: ex/second}\n"
    "    produces: {output: ex/second_amount}\n"
)


def dataset(directory: Path, family: str, year: int) -> None:
    namespace, _, rest = family.partition("/")
    write(
        directory,
        f"{namespace}/parameters/{rest}/{year}.yaml",
        f"family: {family}\ntax_year: {year}\nkind: credit\nsources: [https://example.test/form]\n"
        f'rounding: {{increment: "0.01", mode: half_up}}\namount: "100"\n',
    )


def two_family_form(directory: Path) -> None:
    """The form `ex/benefit` reads `ex/base` and `ex/second`."""
    write_benefit(directory)
    path = directory / "ex/forms/benefit/00-benefit.yaml"
    text = path.read_text().replace(
        "exports: [ex/base_amount]", "exports: [ex/base_amount, ex/second_amount]"
    )
    path.write_text(text + SECOND_STEP)


def checking(directory: Path) -> TaxComputationService:
    capabilities = CapabilityRegistry()
    capabilities.register("core/credit_amount", CreditAmount)
    capabilities.register("ex/half", Half)
    parameters = YamlParameterSource(package_roots(directory), parameter_parsers())
    return TaxComputationService(source(directory), parameters, capabilities)


def years_of(directory: Path) -> list[int]:
    roots: Mapping[Namespace, Path] = package_roots(directory)
    return resolvable_years(roots.values(), source(directory).get_jurisdiction(EX_ON))


def test_the_years_are_the_manifests_first_year_to_the_greatest_dataset_year(
    tmp_path: Path,
) -> None:
    two_family_form(tmp_path)
    province(tmp_path, "[ex/benefit]")
    dataset(tmp_path, "ex/base", 2025)
    dataset(tmp_path, "ex/second", 2025)
    dataset(tmp_path, "ex/second", 2026)

    assert years_of(tmp_path) == [2025, 2026]


def test_a_dataset_for_one_of_two_resolvable_years_fails_naming_the_family_and_the_year(
    tmp_path: Path,
) -> None:
    two_family_form(tmp_path)
    province(tmp_path, "[ex/benefit]")
    dataset(tmp_path, "ex/base", 2025)
    dataset(tmp_path, "ex/second", 2025)
    dataset(tmp_path, "ex/second", 2026)

    with pytest.raises(pytest.fail.Exception, match=r"EX-ON, tax year 2026: .*ex/base"):
        require_every_year_composes(checking(tmp_path), EX_ON, years_of(tmp_path))


def test_every_failing_year_is_reported_not_just_the_first(tmp_path: Path) -> None:
    two_family_form(tmp_path)
    province(tmp_path, "[ex/benefit]")
    dataset(tmp_path, "ex/base", 2025)
    dataset(tmp_path, "ex/second", 2025)
    dataset(tmp_path, "ex/second", 2027)

    failures = composition_failures(checking(tmp_path), EX_ON, years_of(tmp_path))

    assert [line.split(":")[0] for line in failures] == [
        "EX-ON, tax year 2026",
        "EX-ON, tax year 2027",
    ]


def test_a_jurisdiction_whose_every_family_has_every_year_passes(tmp_path: Path) -> None:
    two_family_form(tmp_path)
    province(tmp_path, "[ex/benefit]")
    for year in (2025, 2026):
        dataset(tmp_path, "ex/base", year)
        dataset(tmp_path, "ex/second", year)

    require_every_year_composes(checking(tmp_path), EX_ON, years_of(tmp_path))


# --- the startup composes nothing -------------------------------------------------------------


def test_building_the_engine_composes_no_manifest(monkeypatch: pytest.MonkeyPatch) -> None:
    def refuse(*args: object) -> None:
        raise AssertionError("the engine composed a manifest while building")

    monkeypatch.setattr(TaxComputationService, "compose", refuse)

    assert factory.build_tax_computation() is not None


def test_the_service_has_no_startup_check() -> None:
    assert not hasattr(TaxComputationService, "check")


def test_a_year_is_composed_once_and_the_same_forms_are_returned(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    two_family_form(tmp_path)
    province(tmp_path, "[ex/benefit]")
    dataset(tmp_path, "ex/base", 2025)
    dataset(tmp_path, "ex/second", 2025)
    service = checking(tmp_path)
    first = service.compose(EX_ON, 2025)

    def recomposed(*args: object) -> None:
        raise AssertionError("composed again")

    monkeypatch.setattr(service, "_compose", recomposed)
    assert service.compose(EX_ON, 2025) is first
