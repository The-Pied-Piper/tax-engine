"""Finding parameter parsers by walking a package's modules: nothing lists them."""

from __future__ import annotations

from tax_engine.adapters.outbound.jurisdiction_packages import JurisdictionPackages
from tax_engine.adapters.outbound.parser_modules import parsers_in
from tax_engine.adapters.parameter_parser import ParameterParserRegistry
from tests.jurisdictions.registration_fixtures import ex_on, ex_parse
from tests.jurisdictions.registration_fixtures.ex_parse import parameter_parsers
from tests.jurisdictions.registration_fixtures.ex_parse.parameter_parsers.flat import (
    FLAT,
    FlatParser,
    NotAParser,
)
from tests.jurisdictions.registration_fixtures.ex_parse.parameter_parsers.more.double import (
    DOUBLE,
    DoubleParser,
)


def test_it_finds_every_parser_class_in_every_module_below_the_package() -> None:
    assert parsers_in(parameter_parsers) == [DoubleParser, FlatParser]


def test_a_class_imported_into_another_module_is_found_once_where_it_is_defined() -> None:
    assert parsers_in(parameter_parsers).count(FlatParser) == 1


def test_a_class_declaring_no_kind_is_left_out() -> None:
    assert NotAParser not in parsers_in(parameter_parsers)


def test_a_package_registers_the_parsers_it_walks() -> None:
    registry = ParameterParserRegistry()

    JurisdictionPackages((ex_parse,)).register_parameter_parsers(registry)

    assert registry.identifiers() == {"flat", "double"}
    assert isinstance(registry.for_kind(FLAT), FlatParser)
    assert isinstance(registry.for_kind(DOUBLE), DoubleParser)


def test_a_package_without_a_parameter_parsers_package_contributes_none() -> None:
    registry = ParameterParserRegistry()

    JurisdictionPackages((ex_on,)).register_parameter_parsers(registry)

    assert registry.identifiers() == frozenset()
