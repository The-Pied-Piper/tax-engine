"""Fixtures for the federal Canada tests."""

from __future__ import annotations

import pytest

from tax_calculator.domain.artifact import ArtifactRegistry
from tax_calculator.registrations import JURISDICTIONS


@pytest.fixture
def registry() -> ArtifactRegistry:
    registry = ArtifactRegistry()
    JURISDICTIONS.register(registry)
    return registry
