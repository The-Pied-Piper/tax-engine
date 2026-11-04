"""Finding capabilities by walking a package's modules: nothing lists them."""

from __future__ import annotations

from tax_engine.adapters.outbound.capability_modules import capabilities_in
from tests.jurisdictions.registration_fixtures.ex_cap import capabilities
from tests.jurisdictions.registration_fixtures.ex_cap.capabilities import InInit
from tests.jurisdictions.registration_fixtures.ex_cap.capabilities import levy as levy_module
from tests.jurisdictions.registration_fixtures.ex_cap.capabilities.levy import Levy, Undecorated
from tests.jurisdictions.registration_fixtures.ex_cap.capabilities.more.extra import Extra


def test_it_finds_every_decorated_class_in_every_module_below_the_package() -> None:
    assert capabilities_in(capabilities) == [Extra, InInit, Levy]


def test_a_class_imported_into_another_module_is_found_once_where_it_is_defined() -> None:
    assert capabilities_in(capabilities).count(Levy) == 1


def test_an_undecorated_subclass_of_a_decorated_class_is_left_out() -> None:
    assert Undecorated not in capabilities_in(capabilities)


def test_a_class_bound_to_a_second_name_in_its_module_is_found_once() -> None:
    assert vars(levy_module)["LevyAlias"] is Levy
    assert capabilities_in(capabilities).count(Levy) == 1


def test_a_capability_defined_in_the_package_init_is_found() -> None:
    assert InInit in capabilities_in(capabilities)
