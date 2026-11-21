"""Test support: manifest inputs declared the way the manifest declares them."""

from __future__ import annotations

import re
from collections.abc import Iterable
from pathlib import Path

import tax_engine.jurisdictions.ca_qc
from tax_engine.domain.kinds import RecordListKind
from tax_engine.domain.manifest import InputDeclaration
from tests.federal_forms import FEDERAL_FORMS


def required_fields(kind: RecordListKind) -> tuple[InputDeclaration, ...]:
    """A required declaration for each field of `kind`, in the kind's order."""
    return tuple(InputDeclaration(name=field.identifier, required=True) for field in kind.fields)


def required_inputs(names: Iterable[str]) -> tuple[InputDeclaration, ...]:
    """A required declaration for each of `names`, by identifier, for the `inputs` of a form."""
    return tuple(InputDeclaration(name=name, required=True) for name in sorted(names))


def inputs_without_form(part: Path) -> str:
    """The text of a form's inputs part without its `form:` header.

    A test manifest built from lines of several forms does not declare the form that owns the
    inputs, so the inputs join its default form as the caller's own.
    """
    return re.sub(r"^form:\n  name: .*\n", "", part.read_text(encoding="utf-8"), flags=re.MULTILINE)


# A test-local T1 employment income form declaration that exports line 10100 alone, for a test that
# composes a form reading that line (T2204 line 1) with the real line 10100 part.
T1_LINE_10100_FORM = (
    Path(__file__).parent / "jurisdictions" / "ca" / "support" / "t1_line_10100_form.yaml"
)

# The same two parts by file name, for the Ontario take-home builder, which finds each by name.
T1_LINE_10100_PARTS = (T1_LINE_10100_FORM.name, "t1_employment_income_line_10100.yaml")


# The T1 employment income form's part that declares the salary (line 10100) input, federal and
# Quebec's own. The salary belongs to that form, so a test manifest that copies a step reading it
# copies this part with its `form:` header.
T1_LINE_10100_INPUT = (
    FEDERAL_FORMS / "t1_employment_income" / "t1_employment_income_line_10100_inputs.yaml"
)
# The part that computes line 10100 itself (the step), beside the input part above.
T1_LINE_10100_STEP = T1_LINE_10100_INPUT.with_name("t1_employment_income_line_10100.yaml")
QC_T1_LINE_10100_INPUT = (
    Path(tax_engine.jurisdictions.ca_qc.__file__).parent
    / "manifests"
    / "2025"
    / "t1_employment_income_line_10100_inputs.yaml"
)
