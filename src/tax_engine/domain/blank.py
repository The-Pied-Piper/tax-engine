"""Blank: the value of a line the filer left empty, and how a capability treats one.

A blank is distinct from zero: a form that says to leave a line blank leaves it blank, not zero. A
capability refuses a blank unless the manifest gives a rule for that slot
(`Capability.with_blank_rules`).
"""

from __future__ import annotations

from decimal import Decimal
from enum import Enum

__all__ = ["BLANK", "COMPUTE", "PASS_ON", "Blank", "BlankRule", "Compute", "PassOn"]


class Blank(Enum):
    """The type of the one blank value, `BLANK`; an enum so it is a singleton the type checker
    can tell from every typed value.
    """

    BLANK = "blank"


BLANK = Blank.BLANK
"""The value of an artifact the filer left blank."""


class PassOn(Enum):
    """The type of the one rule `PASS_ON`."""

    PASS_ON = "pass_on"


PASS_ON = PassOn.PASS_ON
"""A blank rule: a blank in this slot makes everything the capability produces blank too."""


class Compute(Enum):
    """The type of the one rule `COMPUTE`."""

    COMPUTE = "compute"


COMPUTE = Compute.COMPUTE
"""A blank rule: a blank in this slot reaches the capability's `compute` as a blank artifact, and
the class decides in code what it means. `compute` may return a blank only in a slot its class
lists in `MAY_BE_BLANK`.
"""

type BlankRule = Decimal | int | PassOn | Compute
"""What a capability does with a blank in one consumed slot, when it may be blank: the fallback
value it takes in its place (a `Decimal`, or an `int` for a count), `PASS_ON`, or `COMPUTE`. A
slot with no rule refuses a blank.
"""
