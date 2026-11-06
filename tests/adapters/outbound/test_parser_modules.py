"""Finding parameter parsers by walking a package's modules: nothing lists them."""

from __future__ import annotations

from tax_engine.adapters.outbound.parameter_parser import is_parser
from tax_engine.adapters.outbound.parser_modules import parsers_in
from tests.jurisdictions.registration_fixtures.ex_parse import parameter_parsers
from tests.jurisdictions.registration_fixtures.ex_parse.parameter_parsers import InInitParser
from tests.jurisdictions.registration_fixtures.ex_parse.parameter_parsers import flat as flat_module
from tests.jurisdictions.registration_fixtures.ex_parse.parameter_parsers.flat import (
    FlatParser,
    Undecorated,
    UndecoratedSubclass,
)
from tests.jurisdictions.registration_fixtures.ex_parse.parameter_parsers.more.double import (
    DoubleParser,
)


def test_it_finds_every_parser_class_in_every_module_below_the_package() -> None:
    assert parsers_in(parameter_parsers) == [DoubleParser, FlatParser, InInitParser]


def test_a_class_imported_into_another_module_is_found_once_where_it_is_defined() -> None:
    assert parsers_in(parameter_parsers).count(FlatParser) == 1


def test_a_class_with_a_kind_but_no_decorator_is_left_out() -> None:
    assert Undecorated not in parsers_in(parameter_parsers)


def test_an_undecorated_subclass_of_a_decorated_class_is_left_out() -> None:
    assert UndecoratedSubclass not in parsers_in(parameter_parsers)


def test_a_parser_defined_in_the_package_init_is_found() -> None:
    assert InInitParser in parsers_in(parameter_parsers)


def test_a_class_bound_to_a_second_name_in_its_module_is_found_once() -> None:
    assert vars(flat_module)["FlatAlias"] is FlatParser
    assert parsers_in(parameter_parsers).count(FlatParser) == 1


def test_is_parser_is_true_only_for_the_decorated_class_itself() -> None:
    assert is_parser(FlatParser)
    assert not is_parser(UndecoratedSubclass)
    assert not is_parser(Undecorated)
