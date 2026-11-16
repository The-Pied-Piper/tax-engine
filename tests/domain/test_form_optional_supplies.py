"""A slot a form marks optional may read a record list that no form supplies.

A capability selection may list `optional` consumed slots (default none: every slot is required).
A record list read through an optional slot that no form supplies is a blank, taken as a blank
input is: the step's blank rule for the slot decides. A supplied one is read as usual, and a slot
not marked optional is still refused when nothing supplies it. Names are made up.
"""

from __future__ import annotations

from decimal import Decimal
from typing import Any

import pytest

from tax_engine.domain.artifact import ArtifactRegistry
from tax_engine.domain.blank import PASS_ON
from tax_engine.domain.errors import BlankNotAllowedError, InvalidCompositionError
from tax_engine.domain.form import FormComposition, FormSet
from tax_engine.domain.manifest import CapabilitySelection, Form
from tax_engine.domain.trace import BlankPassedOnLine
from tax_engine.domain.worksheet import Worksheet
from tax_engine.jurisdictions.core.capabilities.record_total import RecordTotal
from tests.domain.test_form_supplies import (
    FEDERAL_TOTAL,
    INCOME,
    NEUTRAL,
    NEUTRAL_ID,
    RELIEF,
    given,
    levy,
    the_return,
)

D = Decimal
READER = "ex/federal"


def reader(*, optional: tuple[str, ...], rule: bool | None = None) -> FormComposition:
    """The federal form: totals the neutral figure; `optional` names the slots marked optional and
    `rule` gives the `records` slot the blank rule `pass_on`."""
    ruled = bool(optional) if rule is None else rule
    capability = RecordTotal(NEUTRAL, FEDERAL_TOTAL)
    extra: dict[str, Any] = {"optional": optional} if optional else {}
    selection = CapabilitySelection(
        name="core/record_total",
        params={},
        consumes={"records": NEUTRAL_ID},
        produces={"output": FEDERAL_TOTAL.identifier},
        blank={"records": PASS_ON} if ruled else {},
        **extra,
    )
    form = Form(
        name=READER,
        instances=None,
        exports=(FEDERAL_TOTAL.identifier,),
        capabilities=(selection,),
        required=True,
    )
    kinds = ArtifactRegistry()
    for kind in (FEDERAL_TOTAL, NEUTRAL):
        kinds.register(kind.identifier, kind)
    return FormComposition(
        form,
        [capability.with_blank_rules({"records": PASS_ON}) if ruled else capability],
        kinds=kinds,
    )


def sheet(forms: FormSet) -> Worksheet:
    (found,) = forms.compute(*given())[READER]
    return found


def build(federal: FormComposition, *, supplied: bool) -> FormSet:
    suppliers = [levy()] if supplied else []
    return FormSet(
        [federal, *suppliers, the_return()],
        inputs=frozenset({INCOME, RELIEF}),
    )


def test_a_selection_is_required_throughout_by_default() -> None:
    selection = CapabilitySelection(name="a/b", params={}, consumes={}, produces={})

    assert selection.optional == ()


def test_the_optional_slots_are_kept_as_given() -> None:
    selection = CapabilitySelection(
        name="a/b",
        params={},
        consumes={"records": NEUTRAL_ID},
        produces={},
        optional=("records",),
    )

    assert selection.optional == ("records",)


def test_an_optional_import_is_listed_and_is_a_blank_input_of_the_form() -> None:
    form = reader(optional=("records",))

    assert NEUTRAL in form.optional_imports
    assert NEUTRAL in form.blank_inputs


def test_a_required_import_is_neither_optional_nor_blank() -> None:
    form = reader(optional=())

    assert NEUTRAL not in form.optional_imports
    assert NEUTRAL not in form.blank_inputs


def test_an_optional_read_that_nothing_supplies_is_blank_and_passes_on() -> None:
    found = sheet(build(reader(optional=("records",)), supplied=False))

    assert found.get(FEDERAL_TOTAL).is_blank


def test_the_blank_pass_on_is_traced_by_the_existing_blank_line() -> None:
    found = sheet(build(reader(optional=("records",)), supplied=False))

    (line,) = [each for each in found.trace if isinstance(each, BlankPassedOnLine)]
    assert line.output is FEDERAL_TOTAL
    assert line.because == (NEUTRAL,)


def test_an_optional_read_that_is_supplied_gives_the_normal_total() -> None:
    found = sheet(build(reader(optional=("records",)), supplied=True))

    assert found.get(FEDERAL_TOTAL).value == D("600")
    assert not [each for each in found.trace if isinstance(each, BlankPassedOnLine)]


def test_a_read_not_marked_optional_is_still_refused_without_a_supplier() -> None:
    with pytest.raises(InvalidCompositionError, match="ex/federal.*no form exports"):
        build(reader(optional=()), supplied=False)


def test_an_optional_read_without_a_blank_rule_is_refused_as_a_blank() -> None:
    forms = build(reader(optional=("records",), rule=False), supplied=False)

    with pytest.raises(BlankNotAllowedError, match="may not be blank"):
        forms.compute(*given())


def test_an_optional_read_without_a_blank_rule_still_totals_when_supplied() -> None:
    found = sheet(build(reader(optional=("records",), rule=False), supplied=True))

    assert found.get(FEDERAL_TOTAL).value == D("600")
