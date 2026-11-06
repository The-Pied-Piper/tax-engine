from tax_engine.domain.artifact import ArtifactRegistry
from tax_engine.registrations import JURISDICTIONS, artifact_kinds


def test_the_artifact_kinds_hold_every_listed_catalog() -> None:
    expected = ArtifactRegistry()
    JURISDICTIONS.register(expected)

    assert artifact_kinds().identifiers() == expected.identifiers()


def test_each_call_to_the_artifact_kinds_builds_its_own_registry() -> None:
    assert artifact_kinds() is not artifact_kinds()
