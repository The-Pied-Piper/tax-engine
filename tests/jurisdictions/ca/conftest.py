"""Fixtures for the federal Canada tests."""

from __future__ import annotations

import pytest

from tax_engine.domain.artifact import ArtifactRegistry
from tax_engine.registrations import JURISDICTIONS


@pytest.fixture
def registry() -> ArtifactRegistry:
    registry = ArtifactRegistry()
    JURISDICTIONS.register(registry)
    return registry
