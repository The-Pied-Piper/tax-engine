"""Unit tests for JurisdictionCode: an ISO 3166 style code, validated on creation."""

from __future__ import annotations

import pytest

from tax_calculator.domain.errors import InvalidJurisdictionCodeError, ValidationError
from tax_calculator.domain.jurisdiction_code import JurisdictionCode
from tax_calculator.domain.registry import Namespace


@pytest.mark.parametrize(
    "value",
    [
        "CA-ON",  # country + subdivision (ISO 3166-2)
        "CA",  # country only (ISO 3166-1 alpha-2)
        "US-NY",
        "FR-75",  # numeric subdivision
        "GB-ENG",  # three-character subdivision
        "ES-M",  # one-character subdivision
    ],
)
def test_accepts_iso_3166_codes(value: str) -> None:
    code = JurisdictionCode(value)

    assert code.value == value
    assert str(code) == value


@pytest.mark.parametrize(
    "value",
    [
        "",
        "ca-on",  # not canonical; codes are never coerced
        "Ca-ON",
        "CAN-ON",  # alpha-3 country
        "C-ON",
        "CA-",
        "CA-ONTA",  # subdivision longer than three characters
        "CA_ON",
        "CA ON",
        " CA-ON",
        "CA-ON ",
        "CA-ON-X",
        "C1-ON",  # digits are not allowed in the country part
    ],
)
def test_rejects_malformed_codes(value: str) -> None:
    with pytest.raises(InvalidJurisdictionCodeError, match="jurisdiction code"):
        JurisdictionCode(value)


def test_invalid_code_is_a_validation_error() -> None:
    # ValidationError maps to HTTP 422, so a bad code in a request is reported as such.
    assert issubclass(InvalidJurisdictionCodeError, ValidationError)


@pytest.mark.parametrize("value", [None, 1, b"CA-ON"])
def test_rejects_non_string(value: object) -> None:
    with pytest.raises(TypeError, match="must be a str"):
        JurisdictionCode(value)  # type: ignore[arg-type]


def test_codes_are_equal_by_value_and_hashable() -> None:
    assert JurisdictionCode("CA-ON") == JurisdictionCode("CA-ON")
    assert JurisdictionCode("CA-ON") != JurisdictionCode("CA-BC")
    assert len({JurisdictionCode("CA-ON"), JurisdictionCode("CA-ON")}) == 1


def test_is_not_equal_to_a_plain_string() -> None:
    assert JurisdictionCode("CA-ON") != "CA-ON"  # type: ignore[comparison-overlap]


@pytest.mark.parametrize(
    ("value", "namespace"), [("EX-ON", "ex-on"), ("EX", "ex"), ("EX-75", "ex-75")]
)
def test_its_namespace_is_the_code_lower_cased(value: str, namespace: str) -> None:
    assert JurisdictionCode(value).namespace == Namespace(namespace)
