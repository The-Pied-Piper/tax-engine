"""A made-up package that imports a registering module before declaring its NAMESPACE.

The registration runs while this package is still initialising, before NAMESPACE exists, so it
must fail rather than fall back to the enclosing package's `ex` namespace.
"""

from tests.domain.registration_fixtures.with_namespace.late_namespace import things  # noqa: F401

NAMESPACE = "ex-late"
