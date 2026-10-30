"""Unit tests for digits kinds: a number the form asks for as a fixed count of digits, held as text.

A `DigitsKind` is an artifact kind whose value type is `str` and which carries `digits`, the number
of digits the form asks for, such as nine for a business number. An `Artifact` of one holds
exactly that many ASCII digits, kept as entered (a leading zero is a digit), or the empty text for
a box left blank; any other text is an InvalidTextError naming the kind, the number of digits and
the text given. A value that is not a `str` is the artifact's own TypeError. `DigitsKind.declare`
declares a digits kind on a catalog; the number of digits is a positive `int`, else an
InvalidRegistrationError naming the kind. Names are made up; like the record-list tests, the
catalog tests point `ArtifactRegistry.shared` at a fresh registry.
"""

from __future__ import annotations

import re
from decimal import Decimal
from typing import Any, assert_type, cast

import pytest

from tax_engine.domain.artifact import Artifact, ArtifactCatalog, ArtifactKind, ArtifactRegistry
from tax_engine.domain.digits import DigitsKind
from tax_engine.domain.errors import (
    DomainError,
    DuplicateRegistrationError,
    InvalidRegistrationError,
    InvalidTextError,
)
from tax_engine.domain.registry import Namespace

NUMBER = DigitsKind("ex/business_number", digits=9)
SHORT = DigitsKind("ex/filing_number", digits=5)


@pytest.fixture
def fresh(monkeypatch: pytest.MonkeyPatch) -> ArtifactRegistry:
    """A fresh registry that catalogs register into for the duration of one test."""
    registry = ArtifactRegistry()
    monkeypatch.setattr(ArtifactRegistry, "shared", classmethod(lambda cls: registry))
    return registry


def refused(kind: DigitsKind, text: str) -> str:
    """The pattern an InvalidTextError for `text` matches: the kind, its digits, the text."""
    return rf"{re.escape(kind.identifier)}.*{kind.digits} digits.*{re.escape(repr(text))}"


# --- Artifact of a DigitsKind ---------------------------------------------------------------


@pytest.mark.parametrize("text", ["123456789", "000000000", "012345678", "987654320"])
def test_an_artifact_holds_exactly_its_kinds_number_of_digits_as_entered(text: str) -> None:
    artifact = Artifact(NUMBER, text)

    assert artifact.value == text
    assert type(artifact.value) is str


def test_a_leading_zero_is_kept() -> None:
    assert Artifact(NUMBER, "001234567").value == "001234567"


def test_an_artifact_holds_the_empty_text_for_a_box_left_blank() -> None:
    assert Artifact(NUMBER, "").value == ""


def test_artifacts_of_a_digits_kind_are_equal_by_text() -> None:
    assert Artifact(NUMBER, "123456789") == Artifact(NUMBER, "123456789")
    assert Artifact(NUMBER, "123456789") != Artifact(NUMBER, "123456780")
    assert Artifact(NUMBER, "") != Artifact(NUMBER, "000000000")


def test_the_number_of_digits_is_the_kinds_own() -> None:
    assert Artifact(SHORT, "12345").value == "12345"
    assert Artifact(SHORT, "").value == ""
    with pytest.raises(InvalidTextError, match=refused(SHORT, "123456789")):
        Artifact(SHORT, "123456789")


@pytest.mark.parametrize(
    "text",
    [
        "12345678",  # one digit short
        "1234567890",  # one digit over
        "1",
        "12345678a",
        "ABCDEFGHI",
        " 123456789",
        "123456789 ",
        " ",
        "123 456 789",  # spaced as some forms print it
        "123-456-789",
        "+12345678",
        "-12345678",
        "1234.5678",
        "1_2345678",
        "12345678\n",
        "١٢٣٤٥٦٧٨٩",  # ARABIC-INDIC DIGITS
        "１２３４５６７８９",  # FULLWIDTH DIGITS
        "12345678¹",  # SUPERSCRIPT ONE: a digit to str.isdigit, not here
    ],
    ids=lambda text: repr(text),
)
def test_an_artifact_refuses_text_that_is_not_its_number_of_ascii_digits(text: str) -> None:
    with pytest.raises(InvalidTextError, match=refused(NUMBER, text)):
        Artifact(NUMBER, text)


@pytest.mark.parametrize(
    ("value", "name"),
    [(123456789, "int"), (Decimal("123456789"), "Decimal"), (None, "NoneType"), (b"1", "bytes")],
)
def test_a_value_that_is_not_text_is_the_artifacts_type_error(value: object, name: str) -> None:
    with pytest.raises(TypeError, match=rf"business_number must be a str, got {name}"):
        Artifact(NUMBER, cast(Any, value))


def test_an_invalid_text_is_a_domain_error() -> None:
    assert issubclass(InvalidTextError, DomainError)


def test_a_plain_str_kind_is_not_checked_for_digits() -> None:
    # Only a DigitsKind checks its text; the base kind accepts every instance of its value type.
    assert Artifact(ArtifactKind("ex/note", str), "anything").value == "anything"


# --- DigitsKind and DigitsKind.declare ------------------------------------------------------


def test_a_digits_kind_holds_text_and_its_number_of_digits() -> None:
    assert isinstance(NUMBER, ArtifactKind)
    assert NUMBER.identifier == "ex/business_number"
    assert NUMBER.label == "business_number"
    assert NUMBER.value_type is str
    assert NUMBER.non_negative is False
    assert NUMBER.digits == 9


def test_a_catalog_declares_a_digits_kind_in_its_namespace(fresh: ArtifactRegistry) -> None:
    catalog = ArtifactCatalog(Namespace("ex"))

    kind = DigitsKind.declare(catalog, "business_number", digits=9)

    assert_type(kind, DigitsKind)
    assert kind == NUMBER
    assert kind.identifier == "ex/business_number"
    assert kind.value_type is str
    assert kind.digits == 9
    assert catalog.kinds == (kind,)


def test_digits_kinds_are_told_apart_by_their_number_of_digits() -> None:
    # The number of digits is structure: the same identifier with another count is another kind.
    nine = DigitsKind("ex/business_number", digits=9)
    fifteen = DigitsKind("ex/business_number", digits=15)

    assert nine != fifteen
    assert nine == NUMBER
    assert len({nine, NUMBER}) == 1


def test_a_digits_kind_is_not_a_plain_str_kind_of_the_same_identifier() -> None:
    assert NUMBER != ArtifactKind("ex/business_number", str)


def test_declaring_a_digits_kind_registers_nothing(fresh: ArtifactRegistry) -> None:
    DigitsKind.declare(ArtifactCatalog(Namespace("ex")), "business_number", digits=9)

    assert fresh.identifiers() == frozenset()


def test_a_declared_digits_kind_registers_with_its_catalog(fresh: ArtifactRegistry) -> None:
    catalog = ArtifactCatalog(Namespace("ex"))
    count = catalog.declare("partner_count", int)
    kind = DigitsKind.declare(catalog, "business_number", digits=9)
    registry = ArtifactRegistry()

    registry.register_catalog(catalog)

    assert registry.kind("ex/business_number") is kind
    assert registry.kind("ex/partner_count") is count


@pytest.mark.parametrize("digits", [1, 5, 15])
def test_any_positive_number_of_digits_may_be_declared(
    fresh: ArtifactRegistry, digits: int
) -> None:
    kind = DigitsKind.declare(ArtifactCatalog(Namespace("ex")), "some_number", digits=digits)

    assert kind.digits == digits
    assert Artifact(kind, "7" * digits).value == "7" * digits


@pytest.mark.parametrize(
    "digits", [0, -9, True, "9", 9.0, Decimal("9"), None], ids=lambda digits: repr(digits)
)
def test_declare_refuses_a_number_of_digits_that_is_not_a_positive_int(
    fresh: ArtifactRegistry, digits: object
) -> None:
    # `bool` is a subclass of `int` but not a number of digits.
    catalog = ArtifactCatalog(Namespace("ex"))

    with pytest.raises(InvalidRegistrationError, match=r"ex/business_number"):
        DigitsKind.declare(catalog, "business_number", digits=cast(Any, digits))

    assert catalog.kinds == ()


@pytest.mark.parametrize("digits", [0, -1, True, "9"], ids=lambda digits: repr(digits))
def test_a_digits_kind_built_directly_refuses_a_number_of_digits_that_is_not_a_positive_int(
    digits: object,
) -> None:
    with pytest.raises(InvalidRegistrationError, match=r"ex/business_number"):
        DigitsKind("ex/business_number", digits=cast(Any, digits))


def test_declare_refuses_a_local_id_already_declared(fresh: ArtifactRegistry) -> None:
    catalog = ArtifactCatalog(Namespace("ex"))
    first = catalog.declare("business_number", int)

    with pytest.raises(DuplicateRegistrationError, match="'ex/business_number'"):
        DigitsKind.declare(catalog, "business_number", digits=9)

    assert catalog.kinds == (first,)


@pytest.mark.parametrize("local_id", ["", "BusinessNumber", "business-number", "ex/number"])
def test_declare_refuses_a_local_id_that_is_not_snake_case(
    fresh: ArtifactRegistry, local_id: str
) -> None:
    catalog = ArtifactCatalog(Namespace("ex"))

    with pytest.raises(InvalidRegistrationError, match="invalid local id"):
        DigitsKind.declare(catalog, local_id, digits=9)

    assert catalog.kinds == ()


def test_a_catalog_refuses_to_add_a_digits_kind_of_another_namespace(
    fresh: ArtifactRegistry,
) -> None:
    catalog = ArtifactCatalog(Namespace("ex"))

    with pytest.raises(InvalidRegistrationError, match=r"ex-on/business_number.*'ex'"):
        catalog.add(DigitsKind("ex-on/business_number", digits=9))

    assert catalog.kinds == ()


def test_a_digits_kind_may_be_declared_in_a_subdivision_namespace(
    fresh: ArtifactRegistry,
) -> None:
    kind = DigitsKind.declare(ArtifactCatalog(Namespace("ex-on")), "business_number", digits=9)

    assert kind.identifier == "ex-on/business_number"
    assert Artifact(kind, "123456789").value == "123456789"
