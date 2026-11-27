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


# A form that reads another form's export is composed with it: Schedule 8 line A reads the T1's year
# of birth, which `t1_lines_copied_by_provinces` holds.
READS_FORMS = {"schedule_8": "t1_lines_copied_by_provinces"}


def form_parts(*forms: str) -> tuple[Path, ...]:
    """Every part file of the named federal forms, each form's parts in file-name order.

    A form is named by its folder under the `ca` package's `forms` (for example "schedule_8"). A
    form it reads from (`READS_FORMS`) is added after the named ones unless it is named.
    """
    named = list(forms)
    for form in forms:
        needed = READS_FORMS.get(form)
        if needed is not None and needed not in named:
            named.append(needed)
    return tuple(part for form in named for part in sorted((FEDERAL_FORMS / form).glob("*.yaml")))


def form_part_names(*forms: str) -> tuple[str, ...]:
    """The file names of `form_parts`, for a builder that finds each part by name."""
    return tuple(part.name for part in form_parts(*forms))
