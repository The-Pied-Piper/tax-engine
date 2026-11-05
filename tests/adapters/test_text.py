"""The one reader of text: numbers, strings and defaults as the manifest and a request write them.

Reads text by the value type of a kind, never by the kind's class; the finished artifact is
checked by the kind itself.
"""

from __future__ import annotations

from decimal import Decimal
from typing import Any, assert_type

import pytest

from tax_engine.adapters.text import read_artifact, read_default, read_number
from tax_engine.domain.artifact import Artifact, ArtifactKind
from tax_engine.domain.errors import InvalidTextError, NegativeArtifactError
from tax_engine.domain.kinds import (
    AmountKind,
    CountKind,
    DigitsKind,
    RateKind,
    RecordListKind,
    TextKind,
)

D = Decimal
BASE = AmountKind("ex/taxable_base")
NON_NEGATIVE = AmountKind("ex/credit", non_negative=True)
COUNT = CountKind("ex/person_count", non_negative=True)
NUMBER = DigitsKind("ex/business_number", digits=9)
DEPENDANTS = RecordListKind("ex/dependants", fields=(BASE,))


class FlagKind(ArtifactKind[bool]):
    """A kind of a value type the reader has no spelling for."""


def test_the_value_type_is_known_statically() -> None:
    assert_type(read_artifact(BASE, "1"), Artifact[Decimal])
    assert_type(read_artifact(CountKind("ex/count"), "1"), Artifact[int])


@pytest.mark.parametrize(("text", "expected"), [("12.50", D("12.50")), ("-3", D(-3)), ("0", D(0))])
def test_a_decimal_is_a_plain_decimal_number(text: str, expected: Decimal) -> None:
    assert read_number(Decimal, text) == expected
    assert read_artifact(BASE, text) == Artifact(BASE, expected)


@pytest.mark.parametrize("text", ["", " 1", "1e3", "1,5", "abc", "NaN", "1.", "٣", "+5", "1_0"])
def test_text_that_is_not_a_plain_decimal_number_is_refused(text: str) -> None:
    with pytest.raises(InvalidTextError, match="plain decimal number"):
        read_number(Decimal, text)


def test_a_whole_number_is_an_int() -> None:
    assert read_number(int, "-4") == -4
    assert type(read_number(int, "3")) is int
    assert read_artifact(COUNT, "3") == Artifact(COUNT, 3)


@pytest.mark.parametrize("text", ["1.5", "", "two", "0x10"])
def test_text_that_is_not_a_whole_number_is_refused(text: str) -> None:
    with pytest.raises(InvalidTextError, match="whole number"):
        read_number(int, text)


def test_a_decimal_subclass_is_read_as_that_subclass() -> None:
    class Cents(Decimal):
        pass

    assert type(read_number(Cents, "1.25")) is Cents


def test_a_number_of_more_than_the_digits_python_reads_is_too_long() -> None:
    with pytest.raises(InvalidTextError, match="too long"):
        read_number(int, "9" * 5000)


def test_a_value_type_that_is_not_a_number_has_no_spelling_as_a_number() -> None:
    with pytest.raises(InvalidTextError, match="str"):
        read_number(str, "1")


@pytest.mark.parametrize("kind", [NON_NEGATIVE, COUNT])
def test_the_kind_refuses_a_number_below_zero(kind: ArtifactKind[Any]) -> None:
    with pytest.raises(NegativeArtifactError):
        read_artifact(kind, "-1")
    assert read_artifact(kind, "0").value == 0


def test_a_text_kind_reads_the_text_as_written() -> None:
    assert read_artifact(TextKind("ex/person_name"), "  Ada  ").value == "  Ada  "


def test_a_digits_kind_reads_its_digits_as_entered_and_blank_text() -> None:
    assert read_artifact(NUMBER, "012345678") == Artifact(NUMBER, "012345678")
    assert read_artifact(NUMBER, "") == Artifact(NUMBER, "")


def test_a_digits_kind_refuses_other_text() -> None:
    with pytest.raises(InvalidTextError, match="must be 9 digits"):
        read_artifact(NUMBER, "12a")


def test_a_record_list_has_no_spelling_as_text() -> None:
    with pytest.raises(InvalidTextError, match="has no spelling as text"):
        read_artifact(DEPENDANTS, "[]")


def test_a_rate_has_no_spelling_as_text() -> None:
    with pytest.raises(InvalidTextError, match="has no spelling as text"):
        read_artifact(RateKind("ex/credit_rate"), "0.15")


def test_a_kind_of_another_value_type_has_no_spelling_as_text() -> None:
    with pytest.raises(InvalidTextError, match="bool"):
        read_artifact(FlagKind("ex/flag", bool), "true")


def test_a_default_of_none_is_blank() -> None:
    kinds: list[ArtifactKind[Any]] = [BASE, COUNT, NUMBER, DEPENDANTS]
    for kind in kinds:
        assert read_default(kind, None).is_blank


def test_a_default_string_is_read_as_an_artifact_is() -> None:
    assert read_default(BASE, "5") == read_artifact(BASE, "5")
    assert read_default(NUMBER, "123456789") == read_artifact(NUMBER, "123456789")
    with pytest.raises(NegativeArtifactError):
        read_default(NON_NEGATIVE, "-1")


def test_an_empty_list_default_is_refused_for_a_kind_that_is_not_a_record_list() -> None:
    with pytest.raises(InvalidTextError, match="quoted number"):
        read_default(BASE, ())
    with pytest.raises(InvalidTextError, match="string"):
        read_default(NUMBER, ())


def test_a_record_list_reads_an_empty_list_default() -> None:
    artifact = read_default(DEPENDANTS, ())

    assert not artifact.is_blank
    assert artifact.value.records == ()
    assert artifact.value.fields == (BASE,)


def test_a_record_list_refuses_a_string_default() -> None:
    with pytest.raises(InvalidTextError, match="has no spelling as text"):
        read_default(DEPENDANTS, "0")
