"""Class rates: a form's table of classes, each with its rate, its rules and its two factors.

Each class is keyed by its number as printed, an exact `Decimal` so a class such as 10.1 is a
number; it holds its `rate`, whether the half-year rule applies to it or it is exempt, whether
recapture and a terminal loss apply to it or it is excluded, and two factors, the `aiip_factor` and
the `riip_factor`. A class also states whether it has the half-year rule on sale
(`half_year_rule_on_sale`) or not. A class may list `elections`, each a whole `code` above 0 and the
`rate` a row takes when the caller elects that code, such as a reduced or increased rate a taxpayer
elects for a property. The factors are `Fraction`s, the `fraction` kind's values, kept as given: a
form can print a factor of 0 as well as one such as seven eighths. The table holds at least one
class, no class number twice (by value), in the order given; a class it does not list is `None`. The
table also holds the days in a full fiscal period, which a first fiscal period of fewer days is
prorated against.
The code holds no jurisdiction's tables.
"""

from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal
from enum import Enum

from tax_engine.domain.errors import InvalidClassRatesError
from tax_engine.domain.parameters.fraction import Fraction
from tax_engine.domain.parameters.kind import ParameterKind
from tax_engine.domain.parameters.rate import Rate


class HalfYearRule(Enum):
    """Whether the half-year rule applies to a class's net additions or the class is exempt."""

    APPLIES = "applies"
    EXEMPT = "exempt"


class RecaptureAndTerminalLoss(Enum):
    """Whether recapture and a terminal loss apply to a class or the class is excluded."""

    APPLIES = "applies"
    EXCLUDED = "excluded"


class HalfYearRuleOnSale(Enum):
    """Whether a class has the half-year rule on sale (column 19 of a vehicle sold) or not."""

    APPLIES = "applies"
    DOES_NOT_APPLY = "does_not_apply"


@dataclass(frozen=True)
class ClassElection:
    """One election a class lists: its whole `code` above 0 and the `rate` a row takes when the
    caller elects it.

    Anything else is refused when it is built.
    """

    code: int
    rate: Rate

    def __post_init__(self) -> None:
        # bool is an int subclass but not a code.
        if not isinstance(self.code, int) or isinstance(self.code, bool):
            raise TypeError(f"code must be an int, got {type(self.code).__name__}")
        if self.code <= 0:
            raise InvalidClassRatesError(f"code must be above 0, got {self.code}")
        if not isinstance(self.rate, Rate):
            raise TypeError(f"rate must be a Rate, got {type(self.rate).__name__}")


@dataclass(frozen=True)
class ClassRate:
    """One class: its positive `class_number`, its `rate`, its `half_year_rule`, its
    `recapture_and_terminal_loss` and its `aiip_factor` and `riip_factor`, each a `Fraction`, its
    `half_year_rule_on_sale` and its `elections`, none unless given, each code once.

    Anything else is refused when it is built.
    """

    class_number: Decimal
    rate: Rate
    half_year_rule: HalfYearRule
    recapture_and_terminal_loss: RecaptureAndTerminalLoss
    aiip_factor: Fraction
    riip_factor: Fraction
    half_year_rule_on_sale: HalfYearRuleOnSale
    elections: tuple[ClassElection, ...] = ()

    def __post_init__(self) -> None:
        if not isinstance(self.class_number, Decimal):
            raise TypeError(
                f"class_number must be a Decimal, got {type(self.class_number).__name__}"
            )
        if not self.class_number.is_finite():
            raise InvalidClassRatesError(f"class_number must be finite, got {self.class_number}")
        if self.class_number <= 0:
            raise InvalidClassRatesError(f"class_number must be positive, got {self.class_number}")
        if not isinstance(self.rate, Rate):
            raise TypeError(f"rate must be a Rate, got {type(self.rate).__name__}")
        if not isinstance(self.half_year_rule, HalfYearRule):
            raise TypeError(
                f"half_year_rule must be a HalfYearRule, got {type(self.half_year_rule).__name__}"
            )
        if not isinstance(self.recapture_and_terminal_loss, RecaptureAndTerminalLoss):
            raise TypeError(
                "recapture_and_terminal_loss must be a RecaptureAndTerminalLoss, "
                f"got {type(self.recapture_and_terminal_loss).__name__}"
            )
        if not isinstance(self.half_year_rule_on_sale, HalfYearRuleOnSale):
            raise TypeError(
                "half_year_rule_on_sale must be a HalfYearRuleOnSale, "
                f"got {type(self.half_year_rule_on_sale).__name__}"
            )
        self._check_factor("aiip_factor", self.aiip_factor)
        self._check_factor("riip_factor", self.riip_factor)
        if not isinstance(self.elections, tuple):
            raise TypeError(f"elections must be a tuple, got {type(self.elections).__name__}")
        for index, election in enumerate(self.elections):
            if not isinstance(election, ClassElection):
                raise TypeError(f"elections must hold ClassElection, got {type(election).__name__}")
            if any(election.code == earlier.code for earlier in self.elections[:index]):
                raise InvalidClassRatesError(f"election {election.code} is listed more than once")

    def election_rate(self, code: int) -> Rate | None:
        """The rate of the election `code`, or `None` if the class does not list it."""
        for election in self.elections:
            if election.code == code:
                return election.rate
        return None

    @staticmethod
    def _check_factor(name: str, value: Fraction) -> None:
        # A `Fraction` checks its own parts.
        if not isinstance(value, Fraction):
            raise TypeError(f"{name} must be a Fraction, got {type(value).__name__}")


@dataclass(frozen=True)
class ClassRates:
    """At least one `ClassRate`, no class number twice, in the order given, and the positive whole
    number of days in a full fiscal period (`full_year_days`), the 365 a short fiscal period's CCA
    is compared to, and the whole number of days in the longest fiscal period
    (`longest_fiscal_period_days`, at least `full_year_days`), the most a fiscal period may have."""

    classes: tuple[ClassRate, ...]
    full_year_days: int
    longest_fiscal_period_days: int

    def __post_init__(self) -> None:
        if not isinstance(self.classes, tuple):
            raise TypeError(f"classes must be a tuple, got {type(self.classes).__name__}")
        for index, entry in enumerate(self.classes):
            if not isinstance(entry, ClassRate):
                raise TypeError(f"classes[{index}] must be a ClassRate, got {type(entry).__name__}")
        if not self.classes:
            raise InvalidClassRatesError("class rates need at least one class")
        for index, entry in enumerate(self.classes):
            if any(entry.class_number == earlier.class_number for earlier in self.classes[:index]):
                raise InvalidClassRatesError(f"class {entry.class_number} is listed more than once")
        # bool is an int subclass but not a number of days.
        if not isinstance(self.full_year_days, int) or isinstance(self.full_year_days, bool):
            raise TypeError(
                f"full_year_days must be an int, got {type(self.full_year_days).__name__}"
            )
        if self.full_year_days <= 0:
            raise InvalidClassRatesError(
                f"full_year_days must be positive, got {self.full_year_days}"
            )
        if not isinstance(self.longest_fiscal_period_days, int) or isinstance(
            self.longest_fiscal_period_days, bool
        ):
            raise TypeError(
                "longest_fiscal_period_days must be an int, got "
                f"{type(self.longest_fiscal_period_days).__name__}"
            )
        if self.longest_fiscal_period_days < self.full_year_days:
            raise InvalidClassRatesError(
                f"longest_fiscal_period_days must be at least full_year_days "
                f"{self.full_year_days}, got {self.longest_fiscal_period_days}"
            )

    def for_class(self, class_number: Decimal) -> ClassRate | None:
        """The class numbered `class_number`, compared by value, or `None` if it is not listed."""
        for entry in self.classes:
            if entry.class_number == class_number:
                return entry
        return None


CLASS_RATES: ParameterKind[ClassRates] = ParameterKind("class_rates", ClassRates)
