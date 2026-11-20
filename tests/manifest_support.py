"""Test support: manifest inputs declared the way the manifest declares them."""

from __future__ import annotations

import re
from collections.abc import Iterable
from pathlib import Path

from tax_engine.domain.kinds import RecordListKind
from tax_engine.domain.manifest import InputDeclaration


def required_fields(kind: RecordListKind) -> tuple[InputDeclaration, ...]:
    """A required declaration for each field of `kind`, in the kind's order."""
    return tuple(InputDeclaration(name=field.identifier, required=True) for field in kind.fields)


def required_inputs(names: Iterable[str]) -> dict[str, InputDeclaration]:
    """A required declaration for each of `names`, by identifier."""
    return {name: InputDeclaration(name=name, required=True) for name in sorted(names)}


def inputs_without_form(part: Path) -> str:
    """The text of a form's inputs part without its `form:` header.

    A test manifest built from lines of several forms does not declare the form that owns the
    inputs, so the inputs join its default form as the caller's own.
    """
    return re.sub(r"^form:\n  name: .*\n", "", part.read_text(encoding="utf-8"), flags=re.MULTILINE)


# A test-local T1 taxable income form declaration that exports line 10100 alone, for a test that
# composes a form reading that line (T2204 line 1) with the real line 10100 part.
T1_LINE_10100_FORM = (
    Path(__file__).parent / "jurisdictions" / "ca" / "support" / "t1_line_10100_form.yaml"
)

# The same two parts by file name, for the Ontario take-home builder, which finds each by name.
T1_LINE_10100_PARTS = (T1_LINE_10100_FORM.name, "t1_taxable_income_line_10100.yaml")
