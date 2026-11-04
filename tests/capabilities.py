"""The capabilities of the bundled packages, built once per test process for tests to hand on.

The application builds its capabilities once at wiring (`tax_engine.registrations.capabilities`);
a test that needs them takes this one registry so the packages are not walked over and over. A
test that registers its own capabilities builds a private `CapabilityRegistry` instead.
"""

from functools import cache

from tax_engine.domain.capability import CapabilityRegistry
from tax_engine.registrations import capabilities


@cache
def bundled_capabilities() -> CapabilityRegistry:
    """The capabilities of every bundled package; never register into it."""
    return capabilities()
