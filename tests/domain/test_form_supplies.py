"""A form may supply a neutral figure: `Form.supplies`.

A form that declares `exports` may carry `supplies`, a mapping from a neutral derived identifier
(`<ns>/<form_snake>.<label>`, naming a form that need not exist) to one of its own exports. The
engine derives that record-list kind exactly as it derives the kind of a real export, so any form
reads it by that name. Names are made up.

A slot a form marks optional may read a record list that no form supplies. A capability selection
may list `optional` consumed slots (default none: every slot is required). A record list read
through an optional slot that no form supplies is a blank, taken as a blank input is: the step's
blank rule for the slot decides, and a slot with no blank rule is refused when the forms are
composed. A supplied one is read as usual, and a slot not marked optional is still refused when
nothing supplies it.
"""

from __future__ import annotations

from decimal import Decimal
from types import MappingProxyType
from typing import Any

import pytest

from tax_engine.domain.artifact import Artifact, ArtifactRegistry
from tax_engine.domain.blank import PASS_ON
from tax_engine.domain.errors import InvalidCompositionError
from tax_engine.domain.form import FormComposition, FormSet
from tax_engine.domain.kinds import AmountKind, RecordListKind
from tax_engine.domain.manifest import CapabilitySelection, Form
from tax_engine.domain.parameters.datasets import ParameterDataset
from tax_engine.domain.parameters.rounding import NO_ROUNDING
from tax_engine.domain.parameters.rounding_only import ROUNDING_ONLY, RoundingOnly
from tax_engine.domain.trace import BlankPassedOnLine
from tax_engine.domain.worksheet import Worksheet
from tax_engine.jurisdictions.core.capabilities.record_total import RecordTotal
from tax_engine.jurisdictions.core.capabilities.subtract import Subtract
from tests.forms import composition

D = Decimal

EXACT = ParameterDataset(
    "ex/rounding", 2025, ROUNDING_ONLY, RoundingOnly(), NO_ROUNDING, ("https://example.org/r",)
)

INCOME = AmountKind("ex/income")
RELIEF = AmountKind("ex/relief")
TAX = AmountKind("ex-on/tax")
OTHER_TAX = AmountKind("ex-ab/tax")
FEDERAL_TOTAL = AmountKind("ex/federal_total")
NET = AmountKind("ex-on/net")

NEUTRAL_ID = "ex/provincial_tax.amount"
# What the engine derives for the supplied export: one field, that export's kind.
NEUTRAL = RecordListKind(NEUTRAL_ID, fields=(TAX,))
RETURN = "ex-on/return"


def levy(supplies: dict[str, str] | None = None) -> FormComposition:
    """The province's form: income less relief; exports the tax and supplies it neutrally."""
    return composition(
        "ex-on/levy",
        [Subtract(EXACT, INCOME, RELIEF, TAX)],
        exports=[TAX],
        starting=frozenset({INCOME, RELIEF}),
        supplies={NEUTRAL_ID: "ex-on/tax"} if supplies is None else supplies,
    )


def federal(neutral: RecordListKind = NEUTRAL) -> FormComposition:
    """The federal form: reads the neutral figure by its name only."""
    return composition(
        "ex/federal",
        [RecordTotal(neutral, FEDERAL_TOTAL)],
        exports=[FEDERAL_TOTAL],
    )


def the_return() -> FormComposition:
    return composition(
        RETURN,
        [Subtract(EXACT, INCOME, RELIEF, NET)],
        exports=[NET],
        starting=frozenset({INCOME, RELIEF}),
    )


def given() -> tuple[Artifact[Decimal], ...]:
    return (Artifact(INCOME, D("1000")), Artifact(RELIEF, D("400")))


def test_a_form_supplies_nothing_by_default() -> None:
    form = Form(
        name="ex-on/levy", instances=None, exports=("ex-on/tax",), capabilities=(), required=True
    )

    assert dict(form.supplies) == {}


def test_a_forms_supplies_are_kept_and_read_only() -> None:
    form = Form(
        name="ex-on/levy",
        instances=None,
        exports=("ex-on/tax",),
        capabilities=(),
        required=True,
        supplies={NEUTRAL_ID: "ex-on/tax"},
    )

    assert dict(form.supplies) == {NEUTRAL_ID: "ex-on/tax"}
    assert isinstance(form.supplies, MappingProxyType)


def test_the_derived_kinds_include_the_supplied_kind_as_a_record_list_of_the_export() -> None:
    assert NEUTRAL in levy().derived


def test_the_real_derived_kind_of_a_supplying_form_is_still_derived() -> None:
    assert RecordListKind("ex-on/levy.tax", fields=(TAX,)) in levy().derived


def test_a_form_without_supplies_derives_no_neutral_kind() -> None:
    assert NEUTRAL not in levy(supplies={}).derived


def test_the_supplier_runs_first_and_the_reader_computes_its_figure() -> None:
    forms = FormSet([federal(), levy(), the_return()], inputs=frozenset({INCOME, RELIEF}))

    (sheet,) = forms.compute(*given())["ex/federal"]

    assert sheet.get(FEDERAL_TOTAL).value == D("600")


def test_the_supplied_kinds_field_is_the_kind_of_the_supplied_export() -> None:
    other = composition(
        "ex-ab/levy",
        [Subtract(EXACT, INCOME, RELIEF, OTHER_TAX)],
        exports=[OTHER_TAX],
        starting=frozenset({INCOME, RELIEF}),
        supplies={NEUTRAL_ID: "ex-ab/tax"},
    )
    neutral = RecordListKind(NEUTRAL_ID, fields=(OTHER_TAX,))
    forms = FormSet([federal(neutral), other, the_return()], inputs=frozenset({INCOME, RELIEF}))

    (sheet,) = forms.compute(*given())["ex/federal"]

    assert sheet.get(FEDERAL_TOTAL).value == D("600")


def test_without_a_supplier_the_reader_is_refused_naming_the_form() -> None:
    with pytest.raises(InvalidCompositionError, match="ex/federal.*no form exports"):
        FormSet(
            [federal(), levy(supplies={}), the_return()],
            inputs=frozenset({INCOME, RELIEF}),
        )


# --- optional slots ---------------------------------------------------------------------------

READER = "ex/federal"
# The slot marked optional, with the kind its read is a list of (the field of `NEUTRAL`).
OPTIONAL = {"records": TAX.identifier}


def reader(*, optional: dict[str, str], rule: bool | None = None) -> FormComposition:
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

    assert selection.optional == {}


def test_the_optional_slots_are_kept_with_their_declared_kinds() -> None:
    selection = CapabilitySelection(
        name="a/b",
        params={},
        consumes={"records": NEUTRAL_ID},
        produces={},
        optional=OPTIONAL,
    )

    assert selection.optional == {"records": "ex-on/tax"}


def test_an_optional_import_is_listed_but_is_not_a_blank_input_of_the_form() -> None:
    form = reader(optional=OPTIONAL)

    assert NEUTRAL in form.optional_imports
    assert NEUTRAL not in form.blank_inputs


def test_a_required_import_is_neither_optional_nor_blank() -> None:
    form = reader(optional={})

    assert NEUTRAL not in form.optional_imports
    assert NEUTRAL not in form.blank_inputs


def test_an_import_also_read_through_a_list_slot_is_required() -> None:
    listed = CapabilitySelection(
        name="core/sum",
        params={},
        consumes={"parts": (NEUTRAL_ID,)},
        produces={"output": FEDERAL_TOTAL.identifier},
    )
    optional = CapabilitySelection(
        name="core/record_total",
        params={},
        consumes={"records": NEUTRAL_ID},
        produces={"output": FEDERAL_TOTAL.identifier},
        blank={"records": PASS_ON},
        optional=OPTIONAL,
    )
    form = Form(
        name=READER,
        instances=None,
        exports=(FEDERAL_TOTAL.identifier,),
        capabilities=(optional, listed),
        required=True,
    )
    kinds = ArtifactRegistry()
    for kind in (FEDERAL_TOTAL, NEUTRAL):
        kinds.register(kind.identifier, kind)
    both = FormComposition(form, [RecordTotal(NEUTRAL, FEDERAL_TOTAL)], kinds=kinds)

    assert NEUTRAL in both.imports
    assert NEUTRAL not in both.optional_imports


def test_an_optional_read_that_nothing_supplies_is_blank_and_passes_on() -> None:
    found = sheet(build(reader(optional=OPTIONAL), supplied=False))

    assert found.get(FEDERAL_TOTAL).is_blank


def test_the_blank_pass_on_is_traced_by_the_existing_blank_line() -> None:
    found = sheet(build(reader(optional=OPTIONAL), supplied=False))

    (line,) = [each for each in found.trace if isinstance(each, BlankPassedOnLine)]
    assert line.output is FEDERAL_TOTAL
    assert line.because == (NEUTRAL,)


def test_an_optional_read_that_is_supplied_gives_the_normal_total() -> None:
    found = sheet(build(reader(optional=OPTIONAL), supplied=True))

    assert found.get(FEDERAL_TOTAL).value == D("600")
    assert not [each for each in found.trace if isinstance(each, BlankPassedOnLine)]


def test_a_read_not_marked_optional_is_still_refused_without_a_supplier() -> None:
    with pytest.raises(InvalidCompositionError, match="ex/federal.*no form exports"):
        build(reader(optional={}), supplied=False)


def test_an_optional_read_without_a_blank_rule_or_a_supplier_is_refused_when_composed() -> None:
    with pytest.raises(
        InvalidCompositionError, match="ex/federal.*optional slot 'records'.*no blank rule"
    ):
        build(reader(optional=OPTIONAL, rule=False), supplied=False)


def test_an_optional_read_without_a_blank_rule_still_totals_when_supplied() -> None:
    found = sheet(build(reader(optional=OPTIONAL, rule=False), supplied=True))

    assert found.get(FEDERAL_TOTAL).value == D("600")
