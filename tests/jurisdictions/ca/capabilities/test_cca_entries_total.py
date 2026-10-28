"""Unit test that the base of the CCA entries totals is not itself registered."""

from __future__ import annotations

import pytest

from tax_calculator.domain.capability import CapabilityRegistry
from tax_calculator.domain.errors import UnknownRegistrationError


def test_the_base_is_not_registered() -> None:
    with pytest.raises(UnknownRegistrationError):
        CapabilityRegistry.shared().get("ca/cca_entries_total")
