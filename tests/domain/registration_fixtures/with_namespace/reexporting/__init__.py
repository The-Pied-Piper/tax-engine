"""A made-up subpackage without NAMESPACE that re-exports from a registering submodule.

Inheriting the parent's namespace is fine on its own, but importing a registering module from
this `__init__.py` happens while the package is still initialising, so registration fails.
"""

from tests.domain.registration_fixtures.with_namespace.reexporting.things import Thing

__all__ = ["Thing"]
