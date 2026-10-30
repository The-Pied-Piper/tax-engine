"""Blank: the value of a line the filer left empty, and how a capability treats one (design.md §3).

A blank is a value of its own, distinct from zero, an empty list and an empty text: a form that
says to leave a part blank, or not to complete the rest of the form, leaves those lines blank, not
zero. Any artifact can be blank, so
every capability states, for each artifact slot it consumes, what it does with a blank there: it
refuses it (the default), takes a fallback value the capability itself supplies, or passes the
blank on to everything it produces. The rule is the consuming capability's, whether the blank
came from the request or from an upstream capability.
"""

from __future__ import annotations

from decimal import Decimal
from enum import Enum

__all__ = ["BLANK", "PASS_ON", "Blank", "BlankRule", "PassOn"]


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

type BlankRule = Decimal | int | PassOn
"""What a capability does with a blank in one consumed slot, when it may be blank: the fallback
value it takes in its place (a `Decimal`, or an `int` for a count), or `PASS_ON`. A slot with no
rule refuses a blank.
"""
