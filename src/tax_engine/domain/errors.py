"""Errors raised by the domain and application layers.

They carry no HTTP knowledge; `main.py` maps them onto problem+json responses.
"""

from __future__ import annotations

from decimal import Decimal


class DomainError(Exception):
    """Base class for all business-rule violations."""


class NotFoundError(DomainError):
    pass


class ConflictError(DomainError):
    pass


class ValidationError(DomainError):
    pass


class InvalidManifestError(DomainError):
    """A jurisdiction manifest is malformed or breaks a manifest rule (design.md §4)."""


class InvalidRoundingRuleError(DomainError):
    """A rounding rule's parameters are invalid (design.md §3, Rounding)."""


class InvalidJurisdictionCodeError(ValidationError):
    """A jurisdiction code is not in ISO 3166 form (e.g. `CA` or `CA-ON`)."""


class MissingArtifactError(DomainError):
    """No value was given for an artifact that was asked for."""


class DuplicateArtifactError(DomainError):
    """An artifact was given more than one value."""


class NegativeArtifactError(DomainError):
    """An artifact of a kind declared non-negative was given a value below zero.

    Raised by an artifact, it carries the kind's `identifier` and the `value` as produced or given.
    """

    def __init__(
        self, message: str, *, identifier: str | None = None, value: Decimal | int | None = None
    ) -> None:
        super().__init__(message)
        self.identifier = identifier
        self.value = value


class InvalidRecordError(DomainError):
    """A record list's fields are not a list of Decimal or int kinds, or one of its records is not
    a mapping, misses one of its fields or has another key.
    """


class InvalidTextError(DomainError):
    """A text is not what its kind accepts, such as a digits kind given other than its digits."""


class InputAboveBoundError(DomainError):
    """An amount was given above the bound it may not exceed."""


class InputBelowBoundError(DomainError):
    """An amount was given below the bound it may not fall under."""


class InputOutOfRangeError(ValidationError):
    """A code was given that the form's printed codes do not list.

    A ValidationError like `NoAmountForCountError`: the code is the caller's input, so it is
    mapped to 422 with no entry of its own.
    """


class CapabilityContractError(DomainError):
    """A capability's outputs break its contract.

    They are not the artifacts it declares it produces, or one is below zero for a kind declared
    non-negative.
    """


class InvalidBracketScheduleError(DomainError):
    """A bracket schedule's thresholds or rates are invalid."""


class InvalidParameterDataError(DomainError):
    """A parameter dataset is malformed or does not match where it was found."""


class InvalidCreditError(DomainError):
    """A credit amount is invalid."""


class InvalidRateError(DomainError):
    """A rate is not finite or is outside 0..1."""


class InvalidAmountError(DomainError):
    """An amount is not finite or is negative."""


class InvalidClaimReductionError(DomainError):
    """A claim reduction's ceiling or maximum is not finite or is negative."""


class InvalidThresholdRateError(DomainError):
    """A threshold rate's threshold is not finite or is negative, or its rate is zero."""


class InvalidContributionTierError(DomainError):
    """A contribution tier's bounds or maximum are not finite, negative or out of order."""


class InvalidTaperError(DomainError):
    """A taper's figures are not finite, are negative, or its range is not above zero."""


class InvalidAmountByCountError(DomainError):
    """A table of amounts by count is empty, repeats a count or has a bad figure."""


class NoAmountForCountError(ValidationError):
    """A count was given that the table of amounts by count has no row for.

    It is a ValidationError, not a DomainError of its own: the count is the caller's input and
    the table is as printed, so the fault is the request's, and it maps to the same status as any
    other invalid input.
    """


class InvalidFactorError(DomainError):
    """A factor is not finite or is negative."""


class InvalidFractionError(DomainError):
    """A fraction's numerator is negative or its denominator is not positive."""


class InvalidRateTableError(DomainError):
    """A rate table's bounds or rates are invalid, rows are missing, out of order or leave a gap."""


class InvalidClassRatesError(DomainError):
    """A class-rate table's classes are invalid, missing or list a class number twice."""


class InvalidConditionsError(DomainError):
    """A list of conditions is invalid: a count other than 0 or 1, nothing to test, or a test that
    names no figure to compare or compares with two."""


class DuplicateRegistrationError(DomainError):
    """Something was registered under an identifier that is already taken."""


class UnknownRegistrationError(DomainError):
    """Nothing is registered under the identifier that was looked up."""


class InvalidRegistrationError(DomainError):
    """A registration's identifier or namespace is malformed, or no namespace is declared."""


class InvalidCompositionError(DomainError):
    """Capabilities are wired together badly, or a computation got the wrong starting values."""


class InvalidCapabilityError(DomainError):
    """A capability class declares slots its constructor cannot be built from (design.md §3)."""


class InvalidSelectionError(DomainError):
    """A manifest selection does not fill its capability's slots as declared (design.md §4)."""


class AmbiguousManifestError(DomainError):
    """More than one manifest applies to a tax year (design.md §4; §5 rule 6)."""


class InvalidSurchargeTiersError(DomainError):
    """A tier's threshold or rate is invalid, tiers are missing, or thresholds do not increase."""


class InvalidYearAmountsError(DomainError):
    """A table of amounts by year is empty, out of order or has a bad figure."""
