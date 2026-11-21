"""Test support: the real federal forms, assembled from every part file they have.

A test that composes a real federal form (T1 taxable income, Schedule 8 and so on) asks for the
form by its folder name instead of listing its part files, so a line added to the form's parts
reaches every such test without an edit to any of them. The helper supplies the parts only; a
test still writes its own header and, where it wants one, its own form declaration.
"""

from __future__ import annotations

from pathlib import Path

import tax_engine.jurisdictions.ca

FEDERAL_FORMS = Path(tax_engine.jurisdictions.ca.__file__).parent / "forms"


def form_parts(*forms: str) -> tuple[Path, ...]:
    """Every part file of the named federal forms, each form's parts in file-name order.

    A form is named by its folder under the `ca` package's `forms` (for example "schedule_8").
    """
    return tuple(part for form in forms for part in sorted((FEDERAL_FORMS / form).glob("*.yaml")))


def form_part_names(*forms: str) -> tuple[str, ...]:
    """The file names of `form_parts`, for a builder that finds each part by name."""
    return tuple(part.name for part in form_parts(*forms))
