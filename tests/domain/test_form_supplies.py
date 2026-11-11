"""A form may supply a neutral figure: `Form.supplies`.

A form that declares `exports` may carry `supplies`, a mapping from a neutral derived identifier
(`<ns>/<form_snake>.<label>`, naming a form that need not exist) to one of its own exports. The
engine derives that record-list kind exactly as it derives the kind of a real export, so any form
reads it by that name. Names are made up.
"""

from __future__ import annotations

from decimal import Decimal
from types import MappingProxyType

import pytest

from tax_engine.domain.artifact import Artifact
from tax_engine.domain.errors import InvalidCompositionError
from tax_engine.domain.form import FormComposition, FormSet
from tax_engine.domain.kinds import AmountKind, RecordListKind
from tax_engine.domain.manifest import Form
from tax_engine.domain.parameters.datasets import ParameterDataset
from tax_engine.domain.parameters.rounding import NO_ROUNDING
from tax_engine.domain.parameters.rounding_only import ROUNDING_ONLY, RoundingOnly
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
