"""Parameter kinds: a name for a kind of parameter and the type of its values.

Each parameter type declares its kind next to itself (e.g. BRACKETS beside
BracketSchedule), and each capability declares a kind for each of its parameter
slots (e.g. `schedule: BRACKETS`). Data files
state their kind, so readers can check what they found against what was asked.
Adding a kind changes nothing that already exists.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Generic, TypeVar

# Invariant on purpose. PEP 695 syntax would infer covariance from `value_type: type[T]`, and
# mypy would then widen T to accept, say, a brackets parser whose `parse` returns a Credit.
T = TypeVar("T")

_SNAKE_CASE = re.compile(r"[a-z][a-z0-9]*(_[a-z0-9]+)*")


@dataclass(frozen=True)
class ParameterKind(Generic[T]):  # noqa: UP046  (invariant T, see above)
    """A kind of parameter, such as brackets or a credit, and the type its values have.

    Capabilities declare one per parameter slot, and data files name it in `kind:`.
    """

    name: str
    value_type: type[T]

    def __post_init__(self) -> None:
        if not _SNAKE_CASE.fullmatch(self.name):
            raise ValueError(f"invalid parameter kind name {self.name!r}: expected snake_case")
        if not isinstance(self.value_type, type):
            raise TypeError(f"value_type must be a type, got {self.value_type!r}")
