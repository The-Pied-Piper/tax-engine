"""Finding parameter parsers by walking a package's modules: nothing lists them."""

from __future__ import annotations

from tax_engine.adapters.outbound.parser_modules import parsers_in
from tests.jurisdictions.registration_fixtures.ex_parse import parameter_parsers
from tests.jurisdictions.registration_fixtures.ex_parse.parameter_parsers.flat import (
    FlatParser,
    NotAParser,
    UndecoratedSubclass,
)
from tests.jurisdictions.registration_fixtures.ex_parse.parameter_parsers.more.double import (
    DoubleParser,
)


def test_it_finds_every_parser_class_in_every_module_below_the_package() -> None:
    assert parsers_in(parameter_parsers) == [DoubleParser, FlatParser]


def test_a_class_imported_into_another_module_is_found_once_where_it_is_defined() -> None:
    assert parsers_in(parameter_parsers).count(FlatParser) == 1


def test_a_class_declaring_no_kind_is_left_out() -> None:
    assert NotAParser not in parsers_in(parameter_parsers)


def test_an_undecorated_subclass_of_a_decorated_class_is_left_out() -> None:
    assert UndecoratedSubclass not in parsers_in(parameter_parsers)
