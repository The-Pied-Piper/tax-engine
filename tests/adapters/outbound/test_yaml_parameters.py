"""Unit tests for YamlParameterSource itself: finding, resolving and registering parameter datasets.

The source takes a mapping of namespace -> package directory. Family `ex/brackets` for 2025 lives
at `roots[Namespace("ex")] / "parameters" / "brackets" / "2025.yaml"`; the namespace is the part of
the family before the first `/`. Each kind is parsed by the parser registered for it. The kinds
themselves are tested next to their jurisdiction, under tests/jurisdictions.
Values are made up.
"""

from __future__ import annotations

from decimal import Decimal
from pathlib import Path

import pytest

from tax_engine.adapters.outbound.parameter_parser import ParameterParserRegistry
from tax_engine.adapters.outbound.yaml_parameters import YamlParameterSource
from tax_engine.adapters.outbound.yaml_support import YamlNode
from tax_engine.domain.errors import (
    DomainError,
    InvalidParameterDataError,
    NotFoundError,
    UnknownRegistrationError,
)
from tax_engine.domain.parameters.brackets import BRACKETS, Bracket, BracketSchedule
from tax_engine.domain.parameters.credit import CREDIT, Credit
from tax_engine.domain.parameters.datasets import ParameterDataset
from tax_engine.domain.parameters.kind import ParameterKind
from tax_engine.domain.parameters.rounding import NO_ROUNDING
from tax_engine.domain.registry import Namespace
from tax_engine.domain.unit import Unit, UnitCatalog, UnitRegistry
from tax_engine.jurisdictions.core.parameter_parsers.credit import CreditParser
from tests.parameter_source_support import (
    BRACKETS_2025,
    CREDIT_2025,
    EX,
    D,
    roots,
    write,
)
from tests.parameter_source_support import (
    core_parsers as built_in_parsers,
)


def source(directory: Path) -> YamlParameterSource:
    return YamlParameterSource(roots(directory), parsers=built_in_parsers())


FLAT_RATE = ParameterKind("flat_rate", Decimal)


class FlatRateParser:
    """A kind the adapter has never heard of, added purely by registering a parser."""

    kind = FLAT_RATE
    body_keys = frozenset({"rate"})

    def parse(self, document: YamlNode) -> Decimal:
        return document.field("rate").parse_decimal()


def test_new_kinds_need_only_a_registered_parser(tmp_path: Path) -> None:
    write(
        tmp_path,
        "ex/parameters/flat/2025.yaml",
        "family: ex/flat\ntax_year: 2025\nkind: flat_rate\n"
        'sources: [https://example.org]\nrounding: none\nrate: "0.2"\n',
    )
    parsers = built_in_parsers()
    parsers.register_class(FlatRateParser)

    values: Decimal = (
        YamlParameterSource(roots(tmp_path), parsers=parsers).get("ex/flat", 2025, FLAT_RATE).values
    )

    assert values == D("0.2")


def test_a_dataset_may_carry_the_title_the_form_prints(tmp_path: Path) -> None:
    write(tmp_path, "ex/parameters/personal_credit/2025.yaml", CREDIT_2025 + 'title: "maximum"\n')
    write(
        tmp_path, "ex/parameters/other_credit/2025.yaml", CREDIT_2025.replace("personal", "other")
    )

    with_title = source(tmp_path).get("ex/personal_credit", 2025, CREDIT)
    without = source(tmp_path).get("ex/other_credit", 2025, CREDIT)

    assert (with_title.title, without.title) == ("maximum", None)


def test_a_blank_dataset_title_is_refused(tmp_path: Path) -> None:
    write(tmp_path, "ex/parameters/personal_credit/2025.yaml", CREDIT_2025 + 'title: " "\n')

    with pytest.raises(InvalidParameterDataError):
        source(tmp_path).get("ex/personal_credit", 2025, CREDIT)


def unit_registry() -> UnitRegistry:
    catalog = UnitCatalog(Namespace("ex"))
    catalog.declare("crowns")
    registry = UnitRegistry()
    registry.register_catalog(catalog)
    return registry


def source_with_units(directory: Path, units: UnitRegistry | None) -> YamlParameterSource:
    return YamlParameterSource(roots(directory), parsers=built_in_parsers(), units=units)


def test_a_dataset_may_carry_the_unit_its_figures_are_measured_in(tmp_path: Path) -> None:
    write(tmp_path, "ex/parameters/personal_credit/2025.yaml", CREDIT_2025 + "unit: ex/crowns\n")
    write(
        tmp_path, "ex/parameters/other_credit/2025.yaml", CREDIT_2025.replace("personal", "other")
    )
    units = unit_registry()
    source = source_with_units(tmp_path, units)

    with_unit = source.get("ex/personal_credit", 2025, CREDIT)
    without = source.get("ex/other_credit", 2025, CREDIT)

    assert with_unit.unit is units.unit("ex/crowns")
    assert with_unit.unit == Unit("ex/crowns")
    assert without.unit is None


def test_a_dataset_unit_defaults_to_none() -> None:
    dataset = ParameterDataset(
        "ex/personal_credit", 2025, CREDIT, Credit(D("1")), NO_ROUNDING, ("https://x.org",)
    )

    assert dataset.unit is None


@pytest.mark.parametrize("declared", ["ex/nothing", "crowns", '" "', '""'])
def test_an_unknown_bare_or_blank_dataset_unit_is_refused_naming_file_and_identifier(
    tmp_path: Path, declared: str
) -> None:
    write(tmp_path, "ex/parameters/personal_credit/2025.yaml", CREDIT_2025 + f"unit: {declared}\n")

    with pytest.raises(InvalidParameterDataError) as refused:
        source_with_units(tmp_path, unit_registry()).get("ex/personal_credit", 2025, CREDIT)

    message = str(refused.value)
    assert "ex/parameters/personal_credit/2025.yaml" in message
    assert "unit" in message
    assert declared.strip('" ') in message


def test_with_no_unit_registry_a_dataset_naming_a_unit_is_refused(tmp_path: Path) -> None:
    write(tmp_path, "ex/parameters/personal_credit/2025.yaml", CREDIT_2025 + "unit: ex/crowns\n")

    with pytest.raises(InvalidParameterDataError, match=r"2025\.yaml.*ex/crowns"):
        source_with_units(tmp_path, None).get("ex/personal_credit", 2025, CREDIT)


def test_with_no_unit_registry_a_dataset_without_a_unit_still_loads(tmp_path: Path) -> None:
    write(tmp_path, "ex/parameters/personal_credit/2025.yaml", CREDIT_2025)

    assert source_with_units(tmp_path, None).get("ex/personal_credit", 2025, CREDIT).unit is None


def test_requesting_a_kind_without_a_parser_fails(tmp_path: Path) -> None:
    write(tmp_path, "ex/parameters/brackets/2025.yaml", BRACKETS_2025)

    with pytest.raises(UnknownRegistrationError, match="'flat_rate'"):
        source(tmp_path).get("ex/brackets", 2025, FLAT_RATE)


def test_parsers_are_read_from_the_injected_registry(tmp_path: Path) -> None:
    write(tmp_path, "ex/parameters/brackets/2025.yaml", BRACKETS_2025)
    parsers = ParameterParserRegistry()
    parsers.register_class(CreditParser)

    with pytest.raises(UnknownRegistrationError, match="'brackets'"):
        YamlParameterSource(roots(tmp_path), parsers=parsers).get("ex/brackets", 2025, BRACKETS)


def test_by_default_parsers_come_from_the_shared_registry(tmp_path: Path) -> None:
    # The built-in parsers registered themselves in the shared registry when imported.
    write(tmp_path, "ex/parameters/brackets/2025.yaml", BRACKETS_2025)

    result = YamlParameterSource(roots(tmp_path), built_in_parsers()).get(
        "ex/brackets", 2025, BRACKETS
    )

    assert result.values == BracketSchedule(
        (Bracket(D("0"), D("0.10")), Bracket(D("100"), D("0.20")))
    )


def test_absent_year_is_not_found_and_never_carried_forward(tmp_path: Path) -> None:
    write(tmp_path, "ex/parameters/brackets/2025.yaml", BRACKETS_2025)

    with pytest.raises(NotFoundError, match="ex/brackets.*2026"):
        source(tmp_path).get("ex/brackets", 2026, BRACKETS)


def test_absent_family_is_not_found(tmp_path: Path) -> None:
    with pytest.raises(NotFoundError, match="ex/other"):
        source(tmp_path).get("ex/other", 2025, BRACKETS)


def test_each_namespace_resolves_under_its_own_directory(tmp_path: Path) -> None:
    # Directory names need not match namespaces: the mapping decides.
    write(tmp_path, "pkg_one/parameters/brackets/2025.yaml", BRACKETS_2025)
    write(
        tmp_path,
        "pkg_two/parameters/brackets/2025.yaml",
        BRACKETS_2025.replace("family: ex/brackets", "family: ex-two/brackets")
        .replace('"0.10"', '"0.15"')
        .replace('"10.00"', '"15.00"'),
    )
    two_roots = {EX: tmp_path / "pkg_one", Namespace("ex-two"): tmp_path / "pkg_two"}
    parameters = YamlParameterSource(two_roots, parsers=built_in_parsers())

    one = parameters.get("ex/brackets", 2025, BRACKETS)
    two = parameters.get("ex-two/brackets", 2025, BRACKETS)

    assert one.values.brackets[0].rate == D("0.10")
    assert two.values.brackets[0].rate == D("0.15")


def test_family_may_nest_below_the_namespace(tmp_path: Path) -> None:
    write(
        tmp_path,
        "ex/parameters/credits/personal/2025.yaml",
        CREDIT_2025.replace("family: ex/personal_credit", "family: ex/credits/personal"),
    )

    result = source(tmp_path).get("ex/credits/personal", 2025, CREDIT)

    assert result.family == "ex/credits/personal"


def test_files_outside_parameters_are_not_read(tmp_path: Path) -> None:
    write(tmp_path, "ex/brackets/2025.yaml", BRACKETS_2025)

    with pytest.raises(NotFoundError, match="ex/brackets"):
        source(tmp_path).get("ex/brackets", 2025, BRACKETS)


def test_unknown_namespace_is_not_found_and_named(tmp_path: Path) -> None:
    with pytest.raises(NotFoundError, match="namespace 'zz'"):
        source(tmp_path).get("zz/brackets", 2025, BRACKETS)


@pytest.mark.parametrize(
    "family", ["", "EX/brackets", "../brackets", "ex/../x", "/ex/b", "ex/", "ex_on/brackets"]
)
def test_rejects_malformed_family(tmp_path: Path, family: str) -> None:
    with pytest.raises(ValueError, match="parameter family"):
        source(tmp_path).get(family, 2025, BRACKETS)


def test_invalid_data_is_a_domain_error() -> None:
    assert issubclass(InvalidParameterDataError, DomainError)
