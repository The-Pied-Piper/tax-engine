"""Unit tests for FormComposition and FormSet, with made-up `ex/` names.

A computation is a flat set of forms; a form is a peer of the others, never a capability, and none
is special. `FormComposition` is one form wired: an inner `Composition` whose outputs are its
exports and whose inputs are derived: the starting artifacts it reads, plus the fields of its
instances kind if it has one, plus its imports. An export `X` of the form `B` is read
by every form as the derived kind `B.X`, a record list of one field with a record per instance (one
record for a form without an instances list: it has one instance). A form's imports are the
dotted kinds it consumes and nothing in the form produces.

`FormSet` holds the forms. It orders them by their imports (a cycle or an import nothing exports
is an InvalidCompositionError), runs each form once per record of its instances (a form without
instances has one), keeps every form's exports in one store and hands the imports to each run as
starting artifacts. It returns a plain mapping: form name to the worksheet of every instance, in
instance order.

A form may also limit its instances: `max_instances` (at least 1) is the most records the caller
may give, `min_instances` (at least 0) the fewest, and `exclusive_group` names a group of which at
most one form may have instances. A form without an instances list has a default list of one
instance, and the limits apply to its count. The `FormSet` refuses the input otherwise, naming the
form or the group, with a ValidationError; a group that names only one form, or two forms that
always have instances, is an InvalidCompositionError when the set is built.
"""

from __future__ import annotations

from collections.abc import Iterable, Mapping
from decimal import Decimal
from typing import Any, ClassVar

import pytest

from tax_engine.domain.artifact import Artifact, ArtifactKind
from tax_engine.domain.blank import BLANK
from tax_engine.domain.capabilities.record_total import RecordTotal
from tax_engine.domain.capabilities.subtract import Subtract
from tax_engine.domain.capabilities.sum import Sum
from tax_engine.domain.capability import Capability, CapabilityResult
from tax_engine.domain.composition import Composition
from tax_engine.domain.errors import (
    BlankNotAllowedError,
    CapabilityContractError,
    DomainError,
    DuplicateArtifactError,
    InvalidCompositionError,
    MissingArtifactError,
    NotFoundError,
    ValidationError,
)
from tax_engine.domain.form import FormComposition, FormSet
from tax_engine.domain.record_list import RecordList, RecordListKind
from tax_engine.domain.trace import FormInstanceLine, RecordTotalLine, SubtractedLine, TraceLine
from tax_engine.domain.worksheet import Worksheet

D = Decimal

SALES = ArtifactKind("ex/sales", Decimal)
COSTS = ArtifactKind("ex/costs", Decimal)
PROFIT = ArtifactKind("ex/profit", Decimal, non_negative=True)
FEE = ArtifactKind("ex/fee", Decimal)
FEE_TOTAL = ArtifactKind("ex/fee_total", Decimal)
PROFIT_TOTAL = ArtifactKind("ex/profit_total", Decimal)
AUDITED = ArtifactKind("ex/audited", Decimal)
LEVY = ArtifactKind("ex/levy", Decimal)
GRAND = ArtifactKind("ex/grand", Decimal)
NOTE = ArtifactKind("ex/note", str)
BROKEN = ArtifactKind("ex/broken", Decimal)

SHOPS = RecordListKind("ex/shops", fields=(SALES, COSTS))
AUDITS = RecordListKind("ex/audits", fields=(FEE,))
SALES_ONLY = RecordListKind("ex/sales_only", fields=(SALES,))

# What the engine derives for the exports: one field, a record per instance.
SHOP_PROFIT = RecordListKind("ex/shop.profit", fields=(PROFIT,))
AUDIT_AUDITED = RecordListKind("ex/audit.audited", fields=(AUDITED,))
AUDIT_FEE = RecordListKind("ex/audit.fee", fields=(FEE,))
FACT_FEE = RecordListKind("ex/fact.fee", fields=(FEE,))

RETURN = "ex-on/return"
RETURN_GRAND = RecordListKind("ex-on/return.grand", fields=(GRAND,))
FIRST_TOTAL = RecordListKind("ex/first.fee_total", fields=(FEE_TOTAL,))
SECOND_TOTAL = RecordListKind("ex/second.profit_total", fields=(PROFIT_TOTAL,))


class Describe(Capability):
    """Produces `note`, a text: not a kind a record can hold."""

    CONSUMES: ClassVar[Mapping[str, type]] = {"source": Decimal}
    PRODUCES: ClassVar[Mapping[str, type]] = {"note": str}

    def __init__(self, source: ArtifactKind[Decimal], note: ArtifactKind[str]) -> None:
        super().__init__(source=source, note=note)
        self._note = note

    def compute(self, inputs: tuple[Artifact[Any], ...]) -> CapabilityResult:
        return CapabilityResult(outputs=(Artifact(self._note, "x"),), trace=())


class Reject(Capability):
    """Produces `target` as `source`, but raises a DomainError, not a contract error, on 666."""

    CONSUMES: ClassVar[Mapping[str, type]] = {"source": Decimal}
    PRODUCES: ClassVar[Mapping[str, type]] = {"target": Decimal}

    def __init__(self, source: ArtifactKind[Decimal], target: ArtifactKind[Decimal]) -> None:
        super().__init__(source=source, target=target)
        self._source, self._target = source, target

    def compute(self, inputs: tuple[Artifact[Any], ...]) -> CapabilityResult:
        value = self._input(inputs, self._source).value
        if value == 666:
            raise DomainError("666 is not accepted")
        return CapabilityResult(outputs=(Artifact(self._target, value),), trace=())


def shop(name: str = "ex/shop") -> FormComposition:
    """Profit of each shop: sales less costs; exports the profit."""
    return FormComposition(
        name,
        [Subtract(SALES, COSTS, PROFIT)],
        instances=SHOPS,
        exports=[PROFIT],
    )


def audit(name: str = "ex/audit") -> FormComposition:
    """Each audit: the fee less the total profit of all the shops; exports the result."""
    return FormComposition(
        name,
        [RecordTotal(SHOP_PROFIT, PROFIT_TOTAL), Subtract(PROFIT_TOTAL, FEE, AUDITED)],
        instances=AUDITS,
        exports=[AUDITED],
    )


def levy_each(starting: frozenset[ArtifactKind[Any]]) -> FormComposition:
    """Each audit's fee less the starting sales: a form with instances reading a starting kind."""
    return FormComposition(
        "ex/levy",
        [Subtract(SALES, FEE, AUDITED)],
        instances=AUDITS,
        exports=[AUDITED],
        starting=starting,
    )


def flat(
    capabilities: list[Capability],
    *,
    inputs: frozenset[ArtifactKind[Any]],
    outputs: frozenset[ArtifactKind[Any]],
    forms: Iterable[FormComposition] = (),
) -> FormSet:
    """The forms plus a form `ex-on/return` of `capabilities`, which has one instance."""
    default = FormComposition(
        RETURN,
        capabilities,
        exports=sorted(outputs, key=lambda kind: kind.identifier),
        starting=inputs,
    )
    return FormSet([*forms, default], inputs=inputs)


def form_set(*forms: FormComposition) -> FormSet:
    return flat(
        [RecordTotal(AUDIT_AUDITED, GRAND)],
        inputs=frozenset(form.instances for form in forms if form.instances is not None),
        outputs=frozenset({GRAND}),
        forms=forms,
    )


def shops(*pairs: tuple[str, str]) -> Artifact[Any]:
    return Artifact(SHOPS, RecordList(SHOPS.fields, [{SALES: D(s), COSTS: D(c)} for s, c in pairs]))


def audits(*fees: str) -> Artifact[Any]:
    return Artifact(AUDITS, RecordList(AUDITS.fields, [{FEE: D(f)} for f in fees]))


TWO_SHOPS = shops(("12000", "2000"), ("5000", "1000"))
TWO_AUDITS = audits("100", "30")


def values(worksheet: Worksheet, kind: RecordListKind) -> list[Decimal]:
    (field,) = kind.fields
    return [record[field] for record in worksheet.get(kind).value.records]


# --- a form wired: its derived kinds, instance fields and imports --------------------------------


def test_an_exports_derived_kind_is_a_record_list_of_that_one_field() -> None:
    assert shop().derived == (SHOP_PROFIT,)


def test_the_derived_kinds_can_be_built_before_any_selection_is() -> None:
    assert FormComposition.derive("ex/shop", [PROFIT]) == (SHOP_PROFIT,)
    assert FormComposition.derive("ex/audit", [AUDITED, FEE]) == (AUDIT_AUDITED, AUDIT_FEE)


def test_a_form_has_no_imports_when_it_reads_only_its_instance_fields() -> None:
    assert shop().imports == frozenset()


def test_the_imports_are_the_dotted_kinds_the_form_consumes_and_does_not_produce() -> None:
    assert audit().imports == frozenset({SHOP_PROFIT})


def test_the_form_remembers_its_name_instances_and_exports() -> None:
    found = audit()

    assert found.name == "ex/audit"
    assert found.instances is AUDITS
    assert found.exports == (AUDITED,)


def test_the_inner_composition_takes_the_instance_fields_and_the_imports() -> None:
    inner = audit().composition

    assert isinstance(inner, Composition)
    with pytest.raises(InvalidCompositionError, match="missing inputs 'fee', 'shop.profit'"):
        inner.compute()
    inner.compute(
        Artifact(FEE, D(1)),
        Artifact(SHOP_PROFIT, RecordList(SHOP_PROFIT.fields, [{PROFIT: D(5)}])),
    )


def test_an_instance_field_nothing_reads_is_refused_naming_the_form() -> None:
    with pytest.raises(InvalidCompositionError, match="ex/shop.*'costs' is consumed by nothing"):
        FormComposition("ex/shop", [Reject(SALES, PROFIT)], instances=SHOPS, exports=[PROFIT])


def test_a_selection_without_a_producer_is_refused_naming_the_form() -> None:
    with pytest.raises(InvalidCompositionError, match="ex/shop.*no producer for 'fee'"):
        FormComposition(
            "ex/shop",
            [Subtract(SALES, COSTS, PROFIT), Subtract(PROFIT, FEE, AUDITED)],
            instances=SHOPS,
            exports=[AUDITED],
        )


def test_an_export_nothing_in_the_form_produces_is_refused_naming_the_form() -> None:
    with pytest.raises(
        InvalidCompositionError, match="ex/shop.*output 'fee' is produced by nothing"
    ):
        FormComposition(
            "ex/shop", [Subtract(SALES, COSTS, PROFIT)], instances=SHOPS, exports=[PROFIT, FEE]
        )


def test_an_export_that_is_neither_an_amount_a_count_nor_a_record_list_is_not_importable() -> None:
    labelled = FormComposition(
        "ex/labelled", [Describe(SALES, NOTE)], instances=SALES_ONLY, exports=[NOTE]
    )

    assert labelled.exports == (NOTE,)
    assert labelled.derived == ()
    assert FormComposition.derive("ex/labelled", [NOTE, SALES]) == (
        RecordListKind("ex/labelled.sales", fields=(SALES,)),
    )


def test_an_export_that_is_another_forms_export_is_refused() -> None:
    with pytest.raises(InvalidCompositionError, match="ex/audit.*'ex/shop.profit'.*another form"):
        FormComposition(
            "ex/audit",
            [RecordTotal(SHOP_PROFIT, PROFIT_TOTAL)],
            instances=AUDITS,
            exports=[PROFIT_TOTAL, SHOP_PROFIT],
        )


def test_a_form_must_export_something() -> None:
    with pytest.raises(InvalidCompositionError, match="ex/shop.*exports"):
        FormComposition("ex/shop", [Subtract(SALES, COSTS, PROFIT)], instances=SHOPS, exports=[])


def test_instances_that_are_not_a_record_list_are_refused_naming_the_form() -> None:
    with pytest.raises(
        InvalidCompositionError, match="form 'ex/shop': instances 'ex/sales' is not a record list"
    ):
        FormComposition(
            "ex/shop", [Subtract(SALES, COSTS, PROFIT)], instances=SALES, exports=[PROFIT]
        )


# --- the set: order by imports ------------------------------------------------------------------


def test_a_form_that_imports_runs_after_the_form_that_exports_it_even_if_listed_first() -> None:
    first_listed = form_set(audit(), shop())

    assert [found.name for found in first_listed.forms] == ["ex/shop", "ex/audit", RETURN]


def test_forms_that_do_not_import_each_other_run_in_name_order() -> None:
    forms = flat(
        [Subtract(LEVY, FEE_TOTAL, GRAND)],
        inputs=frozenset({SHOPS, LEVY, FEE_TOTAL}),
        outputs=frozenset({GRAND}),
        forms=[shop("ex/zebra"), shop("ex/apple"), shop("ex/mango")],
    )

    assert [found.name for found in forms.forms] == [RETURN, "ex/apple", "ex/mango", "ex/zebra"]


def test_the_order_does_not_depend_on_how_the_forms_were_listed() -> None:
    assert [f.name for f in form_set(shop(), audit()).forms] == [
        f.name for f in form_set(audit(), shop()).forms
    ]


def test_a_cycle_of_imports_is_refused_naming_the_forms_on_it() -> None:
    # shop imports audit.audited, audit imports shop.profit.
    shop_needs_audit = FormComposition(
        "ex/shop",
        [Subtract(SALES, COSTS, PROFIT), RecordTotal(AUDIT_AUDITED, FEE_TOTAL)],
        instances=SHOPS,
        exports=[PROFIT, FEE_TOTAL],
    )
    audit_exporting_total = audit()

    with pytest.raises(InvalidCompositionError, match="cycle") as caught:
        form_set(shop_needs_audit, audit_exporting_total)

    assert "ex/shop" in str(caught.value) and "ex/audit" in str(caught.value)


def test_a_form_outside_the_cycle_is_not_named() -> None:
    shop_needs_audit = FormComposition(
        "ex/shop",
        [Subtract(SALES, COSTS, PROFIT), RecordTotal(AUDIT_AUDITED, FEE_TOTAL)],
        instances=SHOPS,
        exports=[PROFIT, FEE_TOTAL],
    )

    with pytest.raises(InvalidCompositionError, match="cycle") as caught:
        form_set(shop_needs_audit, audit(), shop("ex/bystander"))

    assert "ex/bystander" not in str(caught.value)


def test_an_import_no_form_exports_is_refused_naming_the_form_and_the_kind() -> None:
    with pytest.raises(InvalidCompositionError, match="ex/audit.*no form exports 'shop.profit'"):
        form_set(audit())


def test_an_import_of_another_shape_than_the_export_is_refused() -> None:
    other = RecordListKind("ex/shop.profit", fields=(SALES,))
    needs_sales = FormComposition(
        "ex/audit",
        [RecordTotal(other, PROFIT_TOTAL), Subtract(PROFIT_TOTAL, FEE, AUDITED)],
        instances=AUDITS,
        exports=[AUDITED],
    )

    with pytest.raises(InvalidCompositionError, match="ex/audit.*'shop.profit'"):
        form_set(shop(), needs_sales)


def test_the_returns_import_no_form_exports_is_refused_naming_the_return() -> None:
    with pytest.raises(InvalidCompositionError, match=r"ex-on/return.*'audit.audited'"):
        form_set(shop())


def test_two_forms_of_one_name_are_refused() -> None:
    with pytest.raises(InvalidCompositionError, match="ex/shop.*more than once"):
        form_set(shop(), shop())


def test_a_form_named_like_the_return_is_refused() -> None:
    with pytest.raises(InvalidCompositionError, match="ex-on/return.*more than once"):
        form_set(shop(RETURN), audit())


def test_a_forms_instances_kind_must_be_one_of_the_computations_inputs() -> None:
    with pytest.raises(InvalidCompositionError, match="ex/shop.*'ex/shops'.*not.*input"):
        flat(
            [Subtract(FEE, COSTS, LEVY)],
            inputs=frozenset({FEE, COSTS}),
            outputs=frozenset({LEVY}),
            forms=[shop()],
        )


def test_the_default_form_is_an_ordinary_form_with_one_instance_that_exports_like_any() -> None:
    returns = form_set(shop(), audit()).form(RETURN)

    assert returns.name == RETURN
    assert returns.instances is None
    assert returns.exports == (GRAND,)
    assert returns.derived == (RETURN_GRAND,)
    assert returns.imports == frozenset({AUDIT_AUDITED})


def test_a_form_without_instances_takes_the_starting_artifacts_it_reads() -> None:
    once = FormComposition(
        "ex/once",
        [Subtract(SALES, COSTS, LEVY)],
        exports=[LEVY],
        starting=frozenset({SALES, COSTS, FEE}),
    )

    assert once.inputs == frozenset({SALES, COSTS})  # FEE is a starting artifact it does not read
    assert once.imports == frozenset()


def test_a_form_without_instances_reads_the_starting_artifacts_it_exports_unchanged() -> None:
    once = FormComposition(
        "ex/once",
        [Subtract(SALES, COSTS, LEVY)],
        exports=[LEVY, FEE],
        starting=frozenset({SALES, COSTS, FEE}),
    )

    assert once.inputs == frozenset({SALES, COSTS, FEE})


def test_a_form_without_instances_does_not_take_what_is_not_a_starting_artifact() -> None:
    with pytest.raises(InvalidCompositionError, match="no producer for 'costs'") as caught:
        FormComposition(
            "ex/once", [Subtract(SALES, COSTS, LEVY)], exports=[LEVY], starting=frozenset({SALES})
        )

    assert str(caught.value).startswith("form 'ex/once': ")  # wired before any instance exists
    assert "instance" not in str(caught.value)


def test_a_forms_inputs_are_only_the_starting_artifacts_it_reads() -> None:
    plain = flat(
        [Subtract(SALES, COSTS, LEVY)],
        inputs=frozenset({SALES, COSTS, AUDITS}),
        outputs=frozenset({LEVY}),
        forms=[
            FormComposition("ex/audit", [Reject(FEE, AUDITED)], instances=AUDITS, exports=[AUDITED])
        ],
    )

    inner = plain.form(RETURN).composition
    inner.compute(Artifact(SALES, D(3)), Artifact(COSTS, D(1)))
    with pytest.raises(InvalidCompositionError, match="'audits' is not an input"):
        inner.compute(Artifact(SALES, D(3)), Artifact(COSTS, D(1)), audits("1"))


def test_a_form_with_instances_takes_the_starting_artifacts_it_reads_and_its_fields() -> None:
    levy = levy_each(frozenset({SALES, COSTS}))

    assert levy.inputs == frozenset({SALES, FEE})  # COSTS is a starting artifact it does not read


def test_an_instance_field_that_is_also_a_starting_artifact_is_refused_naming_the_form() -> None:
    with pytest.raises(InvalidCompositionError, match="instance field 'fee'") as caught:
        levy_each(frozenset({SALES, FEE}))

    assert str(caught.value).startswith("form 'ex/levy': ")


def test_each_instance_runs_on_the_starting_artifacts_and_its_own_record() -> None:
    forms = FormSet([levy_each(frozenset({SALES}))], inputs=frozenset({SALES, AUDITS}))

    first, second = forms.compute(Artifact(SALES, D(500)), TWO_AUDITS)["ex/levy"]

    assert first.get(AUDITED).value == D(400)
    assert second.get(AUDITED).value == D(470)
    assert first.get(SALES).value == D(500)  # the starting artifact reaches every instance


def test_a_starting_artifact_is_still_required_when_only_a_form_with_instances_reads_it() -> None:
    forms = FormSet([levy_each(frozenset({SALES}))], inputs=frozenset({SALES, AUDITS}))

    with pytest.raises(InvalidCompositionError, match="missing input 'sales'"):
        forms.compute(TWO_AUDITS)


def test_a_derived_kind_among_the_inputs_is_refused_when_the_set_is_built() -> None:
    with pytest.raises(
        InvalidCompositionError, match="'shop.profit' is exported by a form, not an input"
    ):
        flat(
            [RecordTotal(AUDIT_AUDITED, GRAND)],
            inputs=frozenset({SHOPS, AUDITS, SHOP_PROFIT}),
            outputs=frozenset({GRAND}),
            forms=[shop(), audit()],
        )


def test_a_cycle_between_forms_without_instances_is_refused_naming_them() -> None:
    first = FormComposition("ex/first", [RecordTotal(SECOND_TOTAL, FEE_TOTAL)], exports=[FEE_TOTAL])
    second = FormComposition(
        "ex/second", [RecordTotal(FIRST_TOTAL, PROFIT_TOTAL)], exports=[PROFIT_TOTAL]
    )

    with pytest.raises(InvalidCompositionError, match="cycle") as caught:
        FormSet([first, second], inputs=frozenset())

    assert "ex/first" in str(caught.value) and "ex/second" in str(caught.value)


def test_an_import_no_form_exports_is_refused_for_a_form_without_instances() -> None:
    lonely = FormComposition(
        "ex/lonely", [RecordTotal(SECOND_TOTAL, FEE_TOTAL)], exports=[FEE_TOTAL]
    )

    with pytest.raises(
        InvalidCompositionError, match="ex/lonely.*no form exports 'second.profit_total'"
    ):
        FormSet([lonely], inputs=frozenset())


def test_an_input_no_form_reads_is_refused() -> None:
    with pytest.raises(InvalidCompositionError, match="input 'fee' is consumed by nothing"):
        flat(
            [Subtract(SALES, COSTS, LEVY)],
            inputs=frozenset({SALES, COSTS, FEE}),
            outputs=frozenset({LEVY}),
        )


def test_an_input_one_form_reads_and_another_form_does_not_is_fine() -> None:
    forms = flat(
        [Subtract(SALES, COSTS, LEVY)],
        inputs=frozenset({SALES, COSTS, FEE}),
        outputs=frozenset({LEVY}),
        forms=[
            FormComposition(
                "ex/fees",
                [Reject(FEE, FEE_TOTAL)],
                exports=[FEE_TOTAL],
                starting=frozenset({SALES, COSTS, FEE}),
            )
        ],
    )

    result = forms.compute(Artifact(SALES, D(5)), Artifact(COSTS, D(2)), Artifact(FEE, D(1)))

    assert result[RETURN][0].get(LEVY).value == D(3)
    assert result["ex/fees"][0].get(FEE_TOTAL).value == D(1)
    assert forms.form("ex/fees").inputs == frozenset({FEE})


def test_an_input_that_a_form_also_produces_is_refused() -> None:
    with pytest.raises(InvalidCompositionError, match="input 'levy' is also produced by Subtract"):
        flat(
            [Subtract(SALES, COSTS, LEVY)],
            inputs=frozenset({SALES, COSTS, LEVY}),
            outputs=frozenset({LEVY}),
        )


# --- the run: peers reading each other's exports ------------------------------------------------


def test_a_form_reads_the_exports_of_another_form_on_each_of_its_instances() -> None:
    result = form_set(audit(), shop()).compute(TWO_SHOPS, TWO_AUDITS)

    # total profit 10000 + 4000, less each fee.
    first, second = result["ex/audit"]
    assert first.get(AUDITED).value == D("13900")
    assert second.get(AUDITED).value == D("13970")


def test_the_import_reaches_the_instance_as_a_starting_artifact() -> None:
    result = form_set(shop(), audit()).compute(TWO_SHOPS, TWO_AUDITS)

    worksheet = result["ex/audit"][1]

    assert worksheet.producer_of(SHOP_PROFIT) is None
    assert values(worksheet, SHOP_PROFIT) == [D(10000), D(4000)]


def test_an_export_is_a_record_list_of_one_field_with_a_record_per_instance_in_order() -> None:
    result = form_set(shop(), audit()).compute(TWO_SHOPS, TWO_AUDITS)

    assert result["ex/audit"][0].get(SHOP_PROFIT).value == RecordList(
        (PROFIT,), [{PROFIT: D(10000)}, {PROFIT: D(4000)}]
    )


def test_instance_order_is_the_order_of_the_records_given() -> None:
    swapped = shops(("5000", "1000"), ("12000", "2000"))

    result = form_set(shop(), audit()).compute(swapped, TWO_AUDITS)

    assert values(result["ex/audit"][0], SHOP_PROFIT) == [D(4000), D(10000)]


def test_two_forms_importing_one_export_both_see_all_its_records() -> None:
    review = FormComposition(
        "ex/review",
        [RecordTotal(SHOP_PROFIT, PROFIT_TOTAL), Subtract(PROFIT_TOTAL, FEE, AUDITED)],
        instances=AUDITS,
        exports=[AUDITED],
    )
    forms = flat(
        [RecordTotal(AUDIT_AUDITED, GRAND)],
        inputs=frozenset({SHOPS, AUDITS}),
        outputs=frozenset({GRAND}),
        forms=[shop(), audit(), review],
    )

    result = forms.compute(TWO_SHOPS, TWO_AUDITS)

    assert result["ex/audit"][0].get(AUDITED).value == D("13900")
    assert result["ex/review"][0].get(AUDITED).value == D("13900")
    assert values(result["ex/review"][1], SHOP_PROFIT) == [D(10000), D(4000)]


def test_the_return_form_imports_and_keeps_the_import_with_its_intermediates() -> None:
    result = form_set(shop(), audit()).compute(TWO_SHOPS, TWO_AUDITS)

    returns = result[RETURN][0]

    assert returns.get(GRAND).value == D("13900") + D("13970")
    assert values(returns, AUDIT_AUDITED) == [D("13900"), D("13970")]
    assert returns.producer_of(AUDIT_AUDITED) is None


def test_the_return_form_runs_once_whatever_the_instances() -> None:
    result = form_set(shop(), audit()).compute(TWO_SHOPS, TWO_AUDITS)

    assert result[RETURN] == (result[RETURN][0],)
    assert result[RETURN][0] is result[RETURN][0]


def test_a_form_without_instances_exports_one_record_that_other_forms_read() -> None:
    summary = FormComposition(
        "ex/summary", [RecordTotal(RETURN_GRAND, PROFIT_TOTAL)], exports=[PROFIT_TOTAL]
    )
    # RETURN_GRAND is the default form's export: one record whatever the instances.
    forms = FormSet(
        [*form_set(shop(), audit()).forms, summary],
        inputs=frozenset({SHOPS, AUDITS}),
    )

    result = forms.compute(TWO_SHOPS, TWO_AUDITS)

    (only,) = result["ex/summary"]
    assert values(only, RETURN_GRAND) == [D("27870")]
    assert only.get(PROFIT_TOTAL).value == D("27870")


def test_an_inner_artifact_that_is_not_an_export_is_not_on_the_other_forms_worksheets() -> None:
    result = form_set(shop(), audit()).compute(TWO_SHOPS, TWO_AUDITS)

    for worksheet in (*result["ex/audit"], result[RETURN][0]):
        with pytest.raises(MissingArtifactError, match="no value"):
            worksheet.get(PROFIT)


# --- zero instances -----------------------------------------------------------------------------


def test_no_instances_still_produces_every_export_as_an_empty_record_list() -> None:
    result = form_set(shop(), audit()).compute(shops(), TWO_AUDITS)

    assert result["ex/audit"][0].get(SHOP_PROFIT).value == RecordList((PROFIT,), [])


def test_an_importer_of_an_empty_export_computes_on_the_empty_list() -> None:
    result = form_set(shop(), audit()).compute(shops(), TWO_AUDITS)

    assert result["ex/audit"][0].get(PROFIT_TOTAL).value == D(0)
    assert result[RETURN][0].get(GRAND).value == D("-130")


def test_a_form_of_no_instances_has_no_worksheets_and_no_trace_line() -> None:
    forms = form_set(shop(), audit())
    result = forms.compute(shops(), audits())

    assert result["ex/shop"] == ()
    assert result["ex/audit"] == ()
    assert result[RETURN][0].get(GRAND).value == D(0)
    assert [(line.form, line.position) for line in instance_lines(forms.trace(result))] == [
        (RETURN, 1)
    ]


def test_a_form_of_no_steps_that_exports_its_input_has_a_worksheet_but_no_trace_line() -> None:
    fact = FormComposition("ex/fact", [], exports=[FEE], starting=frozenset({FEE}))
    forms = flat(
        [RecordTotal(FACT_FEE, GRAND)],
        inputs=frozenset({FEE}),
        outputs=frozenset({GRAND}),
        forms=[fact],
    )

    result = forms.compute(Artifact(FEE, D("40")))

    assert len(result["ex/fact"]) == 1
    assert result[RETURN][0].get(GRAND).value == D("40")
    assert [(line.form, line.position) for line in instance_lines(forms.trace(result))] == [
        (RETURN, 1)
    ]


# --- per-instance worksheets, reachable --------------------------------------------------------


def test_every_instance_keeps_its_own_worksheet_by_form_and_position_from_1() -> None:
    result = form_set(shop(), audit()).compute(TWO_SHOPS, TWO_AUDITS)

    assert isinstance(result, dict)
    first, second = result["ex/shop"]
    assert isinstance(first, Worksheet) and isinstance(second, Worksheet)
    assert result["ex/shop"][0] is first
    assert result["ex/shop"][1] is second
    assert first.get(PROFIT).value == D(10000)
    assert second.get(PROFIT).value == D(4000)
    assert first.get(SALES).value == D(12000)
    assert second.get(COSTS).value == D(1000)


def test_a_worksheet_holds_the_instances_starting_fields_and_intermediates_of_that_instance() -> (
    None
):
    result = form_set(shop(), audit()).compute(TWO_SHOPS, TWO_AUDITS)

    worksheet = result["ex/audit"][1]

    assert worksheet.get(FEE).value == D(30)
    assert worksheet.get(PROFIT_TOTAL).value == D(14000)
    assert worksheet.get(AUDITED).value == D(13970)


def test_the_forms_are_named_in_the_order_they_ran_the_default_form_among_them() -> None:
    result = form_set(audit(), shop()).compute(TWO_SHOPS, TWO_AUDITS)

    assert list(result) == ["ex/shop", "ex/audit", RETURN]


def test_the_result_is_a_plain_mapping_of_tuples_of_worksheets() -> None:
    result = form_set(shop(), audit()).compute(TWO_SHOPS, TWO_AUDITS)

    assert type(result) is dict
    assert all(type(found) is tuple for found in result.values())
    assert [len(found) for found in result.values()] == [2, 2, 1]


def test_a_form_the_set_does_not_hold_is_not_found() -> None:
    forms = form_set(shop(), audit())

    assert forms.form("ex/shop").name == "ex/shop"
    with pytest.raises(NotFoundError, match="ex/nowhere"):
        forms.form("ex/nowhere")


def instance_lines(lines: tuple[TraceLine, ...]) -> list[FormInstanceLine]:
    return [line for line in lines if isinstance(line, FormInstanceLine)]


# --- the trace: one line per worksheet, in run order ------------------------------------------


def test_the_trace_has_one_line_per_worksheet_in_run_order_the_default_form_among_them() -> None:
    forms = form_set(audit(), shop())
    result = forms.compute(TWO_SHOPS, TWO_AUDITS)

    lines = forms.trace(result)

    assert all(isinstance(line, FormInstanceLine) for line in lines)
    assert [(line.form, line.position) for line in instance_lines(lines)] == [
        ("ex/shop", 1),
        ("ex/shop", 2),
        ("ex/audit", 1),
        ("ex/audit", 2),
        (RETURN, 1),
    ]
    last = lines[-1]
    assert isinstance(last, FormInstanceLine)
    assert last.lines == result[RETURN][0].trace
    assert [type(line) for line in last.lines] == [RecordTotalLine]


def test_an_instances_line_holds_the_trace_of_that_instances_own_worksheet() -> None:
    forms = form_set(shop(), audit())
    result = forms.compute(TWO_SHOPS, TWO_AUDITS)

    first = forms.trace(result)[0]

    assert isinstance(first, FormInstanceLine)
    assert first.lines == result["ex/shop"][0].trace
    assert [type(line) for line in first.lines] == [SubtractedLine]


# --- the starting artifacts ---------------------------------------------------------------------


def test_the_instances_of_every_form_are_required() -> None:
    with pytest.raises(InvalidCompositionError, match="missing input 'audits'"):
        form_set(shop(), audit()).compute(TWO_SHOPS)


def test_all_missing_instances_are_named() -> None:
    with pytest.raises(InvalidCompositionError, match="missing inputs 'audits', 'shops'"):
        form_set(shop(), audit()).compute()


def test_an_artifact_that_is_not_an_input_is_refused() -> None:
    with pytest.raises(InvalidCompositionError, match="'fee' is not an input"):
        form_set(shop(), audit()).compute(TWO_SHOPS, TWO_AUDITS, Artifact(FEE, D(1)))


def test_an_import_cannot_be_given_as_a_starting_artifact() -> None:
    given = Artifact(SHOP_PROFIT, RecordList(SHOP_PROFIT.fields, []))

    with pytest.raises(InvalidCompositionError, match="'shop.profit'"):
        form_set(shop(), audit()).compute(TWO_SHOPS, TWO_AUDITS, given)


# --- errors name the form and the instance position --------------------------------------------


@pytest.mark.parametrize("position", [1, 2])
def test_a_failure_inside_an_instance_names_the_form_and_the_position(position: int) -> None:
    pairs = [("1000", "100"), ("1000", "100")]
    pairs[position - 1] = ("100", "500")  # a loss: PROFIT is non-negative

    with pytest.raises(CapabilityContractError, match=rf"ex/shop, instance {position}\b") as caught:
        form_set(shop(), audit()).compute(shops(*pairs), TWO_AUDITS)

    assert "profit" in str(caught.value)


def test_a_non_contract_domain_error_keeps_its_class_and_gains_the_names() -> None:
    guarded = FormComposition(
        "ex/shop",
        [Reject(SALES, BROKEN), Subtract(BROKEN, COSTS, PROFIT)],
        instances=SHOPS,
        exports=[PROFIT],
    )

    with pytest.raises(DomainError, match=r"ex/shop, instance 2: 666 is not accepted") as caught:
        form_set(guarded, audit()).compute(shops(("1000", "1"), ("666", "1")), TWO_AUDITS)

    assert type(caught.value) is DomainError


def test_a_failure_in_a_form_that_imports_names_that_form_and_the_instance() -> None:
    guarded = FormComposition(
        "ex/audit",
        [
            Reject(FEE, BROKEN),
            RecordTotal(SHOP_PROFIT, PROFIT_TOTAL),
            Subtract(PROFIT_TOTAL, BROKEN, AUDITED),
        ],
        instances=AUDITS,
        exports=[AUDITED],
    )

    with pytest.raises(DomainError, match=r"ex/audit, instance 2: 666 is not accepted"):
        form_set(shop(), guarded).compute(TWO_SHOPS, audits("100", "666"))


def test_a_failure_of_a_form_without_instances_names_the_form_and_instance_1() -> None:
    boom = flat(
        [Subtract(SALES, COSTS, PROFIT)],
        inputs=frozenset({SALES, COSTS}),
        outputs=frozenset({PROFIT}),
    )

    with pytest.raises(CapabilityContractError) as caught:
        boom.compute(Artifact(SALES, D(1)), Artifact(COSTS, D(2)))

    assert str(caught.value).startswith(f"{RETURN}, instance 1: ")


def once_form() -> FormComposition:
    return FormComposition(
        "ex/once",
        [Subtract(SALES, COSTS, PROFIT)],
        exports=[PROFIT],
        starting=frozenset({SALES, COSTS}),
    )


def test_a_run_error_in_a_form_without_an_instances_list_names_it_and_instance_1() -> None:
    forms = FormSet([once_form()], inputs=frozenset({SALES, COSTS}))

    with pytest.raises(CapabilityContractError, match=r"^ex/once, instance 1: ") as caught:
        forms.compute(Artifact(SALES, D(1)), Artifact(COSTS, D(2)))  # a loss: PROFIT is >= 0

    assert "profit" in str(caught.value)


def test_a_wiring_error_in_a_form_without_an_instances_list_names_the_form_only() -> None:
    with pytest.raises(InvalidCompositionError, match=r"^form 'ex/once': ") as caught:
        FormComposition(
            "ex/once",
            [Subtract(SALES, COSTS, PROFIT)],
            exports=[PROFIT],
            starting=frozenset({SALES}),
        )

    assert "instance" not in str(caught.value)


def test_the_trace_of_a_form_without_an_instances_list_has_one_line_at_position_1() -> None:
    forms = FormSet([once_form()], inputs=frozenset({SALES, COSTS}))
    result = forms.compute(Artifact(SALES, D(5)), Artifact(COSTS, D(2)))

    (line,) = forms.trace(result)

    assert isinstance(line, FormInstanceLine)
    assert (line.form, line.position) == ("ex/once", 1)
    assert line.lines == result["ex/once"][0].trace


# --- a set of one form without instances behaves as the bare composition -----------------------


def lone_set() -> FormSet:
    return flat(
        [Subtract(SALES, COSTS, LEVY)],
        inputs=frozenset({SALES, COSTS}),
        outputs=frozenset({LEVY}),
    )


def lone_composition() -> Composition:
    return Composition(
        [Subtract(SALES, COSTS, LEVY)],
        inputs=frozenset({SALES, COSTS}),
        outputs=frozenset({LEVY}),
    )


def test_a_set_of_one_form_without_instances_computes_what_the_composition_does() -> None:
    given = (Artifact(SALES, D(10)), Artifact(COSTS, D(4)))

    result = lone_set().compute(*given)

    assert result[RETURN][0].get(LEVY) == lone_composition().compute(*given).get(LEVY)
    assert result[RETURN][0].trace == lone_composition().compute(*given).trace
    assert list(result) == [RETURN]


def test_its_starting_kind_errors_are_the_compositions() -> None:
    for arguments in ((), (Artifact(SALES, D(1)),), (Artifact(FEE, D(1)),)):
        with pytest.raises(InvalidCompositionError) as bare:
            lone_composition().compute(*arguments)
        with pytest.raises(InvalidCompositionError) as wrapped:
            lone_set().compute(*arguments)
        assert str(wrapped.value) == str(bare.value)


def test_its_wiring_errors_are_those_of_the_composition_prefixed_with_the_form() -> None:
    with pytest.raises(InvalidCompositionError) as bare:
        Composition(
            [Subtract(SALES, COSTS, LEVY)], inputs=frozenset({SALES}), outputs=frozenset({LEVY})
        )
    with pytest.raises(InvalidCompositionError) as wrapped:
        flat(
            [Subtract(SALES, COSTS, LEVY)],
            inputs=frozenset({SALES}),
            outputs=frozenset({LEVY}),
        )

    assert str(wrapped.value) == f"form {RETURN!r}: {bare.value}"


def test_that_forms_composition_is_the_one_the_bare_wiring_would_give() -> None:
    assert [type(c) for c in lone_set().form(RETURN).composition.order] == [Subtract]


# --- two starting values of one kind -----------------------------------------------------------


def test_two_starting_values_for_a_return_input_are_refused_as_the_worksheet_does() -> None:
    twice = (Artifact(SALES, D(10)), Artifact(SALES, D(11)), Artifact(COSTS, D(4)))

    with pytest.raises(DuplicateArtifactError, match="two starting values for 'sales'") as bare:
        lone_composition().compute(*twice)
    with pytest.raises(DuplicateArtifactError) as wrapped:
        lone_set().compute(*twice)

    assert str(wrapped.value) == str(bare.value)


def test_the_kind_named_is_the_first_given_that_is_repeated_not_the_first_to_repeat() -> None:
    given = (
        Artifact(SALES, D(10)),
        Artifact(COSTS, D(4)),
        Artifact(COSTS, D(5)),
        Artifact(SALES, D(11)),
    )

    with pytest.raises(DuplicateArtifactError) as refused:
        lone_set().compute(*given)

    assert str(refused.value) == "two starting values for 'sales'"


def test_distinct_starting_values_leave_the_result_and_its_trace_as_the_bare_wiring() -> None:
    given = (Artifact(SALES, D(10)), Artifact(COSTS, D(4)))

    result = lone_set().compute(*given)

    assert result[RETURN][0].trace == lone_composition().compute(*given).trace


def test_two_starting_values_for_a_forms_instances_are_refused() -> None:
    with pytest.raises(DuplicateArtifactError, match="two starting values for 'shops'"):
        form_set(shop(), audit()).compute(TWO_SHOPS, shops(("1", "1")), TWO_AUDITS)


def test_two_starting_values_are_refused_even_when_the_kind_is_not_an_input() -> None:
    with pytest.raises(DuplicateArtifactError, match="two starting values for 'fee'"):
        form_set(shop(), audit()).compute(
            TWO_SHOPS, TWO_AUDITS, Artifact(FEE, D(1)), Artifact(FEE, D(2))
        )


# --- limits: a maximum instance count and exclusive groups --------------------------------------


def side(
    name: str,
    *,
    maximum: int | None = None,
    group: str | None = None,
    minimum: int | None = None,
) -> FormComposition:
    """A form of its own instances kind `<name>s` (sales and costs) that exports its profit."""
    kind = RecordListKind(f"{name}s", fields=(SALES, COSTS))
    return FormComposition(
        name,
        [Subtract(SALES, COSTS, PROFIT)],
        instances=kind,
        exports=[PROFIT],
        max_instances=maximum,
        exclusive_group=group,
        min_instances=minimum,
    )


def single(name: str, **limits: Any) -> FormComposition:
    """A form without an instances list (one instance) that exports the profit."""
    return FormComposition(
        name,
        [Subtract(SALES, COSTS, PROFIT)],
        exports=[PROFIT],
        starting=frozenset({SALES, COSTS}),
        **limits,
    )


ONCE_GIVEN = (Artifact(SALES, D(10)), Artifact(COSTS, D(4)))


def once_set(*forms: FormComposition) -> FormSet:
    """The forms plus a form `ex-on/return` that totals the profit of the first.

    Its inputs are sales and costs (for forms without an instances list) and the instances kind
    of each form that has one.
    """
    derived = RecordListKind(f"{forms[0].name}.profit", fields=(PROFIT,))
    return flat(
        [RecordTotal(derived, GRAND)],
        inputs=frozenset(
            {SALES, COSTS} | {form.instances for form in forms if form.instances is not None}
        ),
        outputs=frozenset({GRAND}),
        forms=forms,
    )


def sides(form: FormComposition, count: int) -> Artifact[Any]:
    """`count` instances of `form`, each of sales 10 and costs 4."""
    kind = form.instances
    assert kind is not None
    return Artifact(kind, RecordList(kind.fields, [{SALES: D(10), COSTS: D(4)}] * count))


def copies(name: str, *, group: str | None = None) -> FormComposition:
    """A form of up to one copy whose copies carry no figures: it reads sales and costs as given."""
    return FormComposition(
        name,
        [Subtract(SALES, COSTS, PROFIT)],
        instances=RecordListKind(f"{name}_copies", fields=()),
        exports=[PROFIT],
        starting=frozenset({SALES, COSTS}),
        max_instances=1,
        min_instances=0,
        exclusive_group=group,
    )


def copy_list(form: FormComposition, count: int) -> Artifact[Any]:
    """`count` empty copies of `form`."""
    kind = form.instances
    assert kind is not None
    return Artifact(kind, RecordList(kind.fields, [{}] * count))


def side_set(*forms: FormComposition) -> FormSet:
    """The forms plus a form `ex-on/return` that totals the profit of the first.

    Its inputs are the instances kinds of the forms that have an instances list.
    """
    derived = RecordListKind(f"{forms[0].name}.profit", fields=(PROFIT,))
    return flat(
        [RecordTotal(derived, GRAND)],
        inputs=frozenset(form.instances for form in forms if form.instances is not None),
        outputs=frozenset({GRAND}),
        forms=forms,
    )


def grand(found: dict[str, tuple[Worksheet, ...]]) -> Decimal:
    (worksheet,) = found[RETURN]
    return worksheet.get(GRAND).value


def run_sides(*given: tuple[FormComposition, int], forms: tuple[FormComposition, ...]) -> Decimal:
    return grand(side_set(*forms).compute(*(sides(form, count) for form, count in given)))


def test_a_form_has_no_limits_by_default() -> None:
    assert shop().max_instances is None
    assert shop().exclusive_group is None


def test_the_form_remembers_its_maximum_and_group() -> None:
    found = side("ex/one", maximum=3, group="ex/either")

    assert found.max_instances == 3
    assert found.exclusive_group == "ex/either"


@pytest.mark.parametrize("bad", [0, -1])
def test_a_maximum_below_one_is_refused_naming_the_form(bad: int) -> None:
    with pytest.raises(InvalidCompositionError, match=rf"form 'ex/one'.*max_instances.*{bad}"):
        side("ex/one", maximum=bad)


def test_a_boolean_maximum_is_refused_naming_the_form() -> None:
    with pytest.raises(InvalidCompositionError, match=r"form 'ex/one'.*max_instances.*integer"):
        side("ex/one", maximum=True)


def test_the_default_form_is_an_ordinary_form_without_limits() -> None:
    found = form_set(shop(), audit()).form(RETURN)

    assert found.max_instances is None
    assert found.exclusive_group is None


def test_the_form_remembers_its_minimum() -> None:
    assert shop().min_instances is None
    assert side("ex/one", minimum=2).min_instances == 2


@pytest.mark.parametrize("bad", [True, "1", 1.5])
def test_a_non_integer_minimum_is_refused_naming_the_form(bad: Any) -> None:
    with pytest.raises(InvalidCompositionError, match=r"form 'ex/one'.*min_instances.*integer"):
        side("ex/one", minimum=bad)


def test_a_negative_minimum_is_refused_naming_the_form() -> None:
    with pytest.raises(InvalidCompositionError, match=r"form 'ex/one'.*min_instances.*at least 0"):
        side("ex/one", minimum=-1)


def test_a_minimum_above_the_maximum_is_refused_naming_the_form() -> None:
    with pytest.raises(
        InvalidCompositionError, match=r"form 'ex/one': min_instances 3 is above max_instances 2"
    ):
        side("ex/one", minimum=3, maximum=2)


@pytest.mark.parametrize("bad", ["", "either", "ex/Either", "ex/a.b"])
def test_a_malformed_group_is_refused_naming_the_form(bad: str) -> None:
    with pytest.raises(InvalidCompositionError, match=rf"^form 'ex/one': exclusive_group '{bad}'"):
        side("ex/one", group=bad)


# A form without an instances list has a default list of one instance: limits apply to count 1.


@pytest.mark.parametrize(
    "limit",
    [
        {"max_instances": 1},
        {"max_instances": 4},
        {"min_instances": 0},
        {"min_instances": 1},
        {"min_instances": 1, "max_instances": 1},
        {"exclusive_group": "ex/either"},
    ],
)
def test_a_limit_a_default_list_can_meet_is_accepted(limit: dict[str, Any]) -> None:
    once = single("ex/once", **limit)

    assert once.instances is None
    for name, value in limit.items():
        assert getattr(once, name) == value


def test_a_minimum_above_one_on_a_default_list_is_refused_naming_the_form() -> None:
    with pytest.raises(InvalidCompositionError) as caught:
        single("ex/once", min_instances=2)

    assert str(caught.value) == (
        "form 'ex/once': min_instances 2 can never hold: "
        "a form without an instances list has one instance"
    )


def test_a_default_list_form_within_its_limits_computes() -> None:
    once = single("ex/once", min_instances=1, max_instances=1)

    assert grand(once_set(once).compute(*ONCE_GIVEN)) == D(6)


def test_a_declared_list_with_exactly_one_instance_meets_min_one_max_one() -> None:
    exact = side("ex/exact", minimum=1, maximum=1)

    assert run_sides((exact, 1), forms=(exact,)) == D(6)
    with pytest.raises(
        ValidationError, match=r"^form 'ex/exact' allows at most 1 instance\(s\), got 2"
    ):
        run_sides((exact, 2), forms=(exact,))
    with pytest.raises(
        ValidationError, match=r"^form 'ex/exact' needs at least 1 instance\(s\), got 0"
    ):
        run_sides((exact, 0), forms=(exact,))


def test_min_alone_and_min_with_max_accept_counts_in_range() -> None:
    low = side("ex/low", minimum=2)
    band = side("ex/band", minimum=2, maximum=3)

    assert run_sides((low, 2), forms=(low,)) == D(12)
    assert run_sides((low, 5), forms=(low,)) == D(30)
    assert run_sides((band, 2), forms=(band,)) == D(12)
    assert run_sides((band, 3), forms=(band,)) == D(18)
    with pytest.raises(
        ValidationError, match=r"^form 'ex/band' allows at most 3 instance\(s\), got 4"
    ):
        run_sides((band, 4), forms=(band,))


def test_fewer_instances_than_the_minimum_are_refused_naming_the_form() -> None:
    low = side("ex/low", minimum=2)

    with pytest.raises(
        ValidationError, match=r"^form 'ex/low' needs at least 2 instance\(s\), got 1"
    ):
        run_sides((low, 1), forms=(low,))


def test_a_declared_empty_list_is_refused_by_a_minimum_of_one() -> None:
    low = side("ex/low", minimum=1)

    with pytest.raises(
        ValidationError, match=r"^form 'ex/low' needs at least 1 instance\(s\), got 0"
    ):
        run_sides((low, 0), forms=(low,))


def test_a_minimum_of_zero_allows_an_empty_list() -> None:
    zero = side("ex/zero", minimum=0)

    assert run_sides((zero, 0), forms=(zero,)) == D(0)


def test_the_minimum_is_checked_before_any_form_runs() -> None:
    low, free = side("ex/low", minimum=2), side("ex/free")

    with pytest.raises(
        ValidationError, match=r"^form 'ex/low' needs at least 2 instance\(s\), got 1"
    ):
        side_set(low, free).compute(sides(low, 1), sides(free, 1))


def test_a_default_list_form_claims_its_group_against_a_declared_one() -> None:
    once, declared = (
        single("ex/once", exclusive_group="ex/either"),
        side("ex/declared", group="ex/either"),
    )
    found = once_set(once, declared)

    with pytest.raises(
        ValidationError,
        match=(
            r"^forms 'ex/declared' and 'ex/once' both have instances, "
            "but are in exclusive group 'ex/either'$"
        ),
    ):
        found.compute(*ONCE_GIVEN, sides(declared, 1))
    assert grand(found.compute(*ONCE_GIVEN, sides(declared, 0))) == D(6)


def test_a_group_of_two_default_list_forms_is_refused_when_the_set_is_built() -> None:
    first = single("ex/first", exclusive_group="ex/either")
    second = single("ex/second", exclusive_group="ex/either")

    with pytest.raises(InvalidCompositionError) as caught:
        once_set(first, second)

    assert str(caught.value) == (
        "exclusive group 'ex/either': forms 'ex/first' and 'ex/second' can never hold: "
        "each always has at least one instance"
    )


def test_a_group_of_two_forms_with_a_minimum_of_one_is_refused_when_the_set_is_built() -> None:
    first = side("ex/first", group="ex/either", minimum=1)
    second = side("ex/second", group="ex/either", minimum=1)

    with pytest.raises(InvalidCompositionError) as caught:
        side_set(first, second)

    assert str(caught.value) == (
        "exclusive group 'ex/either': forms 'ex/first' and 'ex/second' can never hold: "
        "each always has at least one instance"
    )


def test_a_form_whose_copies_carry_no_figures_runs_once_per_copy_on_the_shared_inputs() -> None:
    once = copies("ex/once")

    found = once_set(once).compute(*ONCE_GIVEN, copy_list(once, 1))

    assert grand(found) == D(6)
    assert len(found["ex/once"]) == 1


def test_a_form_whose_copies_carry_no_figures_does_not_run_for_an_empty_list() -> None:
    once = copies("ex/once")

    found = once_set(once).compute(*ONCE_GIVEN, copy_list(once, 0))

    assert grand(found) == D(0)
    assert found["ex/once"] == ()


def test_two_forms_with_empty_copies_in_one_group_hold_when_only_one_has_a_copy() -> None:
    first = copies("ex/first", group="ex/either")
    second = copies("ex/second", group="ex/either")
    found = once_set(first, second)

    assert grand(found.compute(*ONCE_GIVEN, copy_list(first, 1), copy_list(second, 0))) == D(6)
    assert grand(found.compute(*ONCE_GIVEN, copy_list(first, 0), copy_list(second, 1))) == D(0)
    with pytest.raises(
        ValidationError,
        match=r"^forms 'ex/first' and 'ex/second' both have instances, but are in exclusive group",
    ):
        found.compute(*ONCE_GIVEN, copy_list(first, 1), copy_list(second, 1))


def test_a_group_with_one_minimum_of_one_beside_a_free_form_is_allowed() -> None:
    first = side("ex/first", group="ex/either", minimum=1)
    second = side("ex/second", group="ex/either", minimum=0)

    assert run_sides((first, 1), (second, 0), forms=(first, second)) == D(6)
    with pytest.raises(
        ValidationError,
        match=(
            r"^forms 'ex/first' and 'ex/second' both have instances, "
            "but are in exclusive group 'ex/either'$"
        ),
    ):
        side_set(first, second).compute(sides(first, 1), sides(second, 1))


def test_more_instances_than_the_maximum_are_refused_naming_the_form() -> None:
    only = side("ex/only", maximum=1)

    with pytest.raises(
        ValidationError, match=r"^form 'ex/only' allows at most 1 instance\(s\), got 2"
    ):
        side_set(only).compute(sides(only, 2))


def test_instances_up_to_the_maximum_are_computed() -> None:
    three = side("ex/three", maximum=3)

    assert run_sides((three, 3), forms=(three,)) == D(18)
    assert run_sides((three, 1), forms=(three,)) == D(6)
    assert run_sides((three, 0), forms=(three,)) == D(0)


def test_the_maximum_applies_to_the_form_that_has_it_only() -> None:
    one, free = side("ex/one", maximum=1), side("ex/free")

    assert run_sides((one, 1), (free, 5), forms=(one, free)) == D(6)


def test_the_form_over_its_maximum_is_the_one_named() -> None:
    one, free = side("ex/one", maximum=1), side("ex/free")

    with pytest.raises(
        ValidationError, match=r"^form 'ex/one' allows at most 1 instance\(s\), got 2"
    ):
        side_set(one, free).compute(sides(one, 2), sides(free, 9))


def test_a_limit_breach_wins_over_an_earlier_form_that_would_fail_and_nothing_runs() -> None:
    kind = RecordListKind("ex/bads", fields=(SALES,))
    bad = FormComposition("ex/bad", [Reject(SALES, PROFIT)], instances=kind, exports=[PROFIT])
    over = side("ex/over", maximum=1)
    found = side_set(bad, over)
    given = Artifact(kind, RecordList(kind.fields, [{SALES: D(666)}]))

    with pytest.raises(
        ValidationError, match=r"^form 'ex/over' allows at most 1 instance\(s\), got 2$"
    ):
        found.compute(given, sides(over, 2))
    with pytest.raises(DomainError, match=r"^ex/bad, instance 1: 666 is not accepted$"):
        found.compute(given, sides(over, 1))


def test_two_forms_of_a_group_that_both_have_instances_are_refused_naming_both_and_the_group() -> (
    None
):
    first, second = side("ex/first", group="ex/either"), side("ex/second", group="ex/either")

    with pytest.raises(ValidationError) as caught:
        side_set(first, second).compute(sides(first, 1), sides(second, 2))

    assert str(caught.value) == (
        "forms 'ex/first' and 'ex/second' both have instances, "
        "but are in exclusive group 'ex/either'"
    )


def test_one_form_of_a_group_with_instances_and_the_other_without_is_allowed() -> None:
    first, second = side("ex/first", group="ex/either"), side("ex/second", group="ex/either")

    assert run_sides((first, 2), (second, 0), forms=(first, second)) == D(12)
    assert run_sides((first, 0), (second, 2), forms=(first, second)) == D(0)


def test_no_instances_of_any_form_of_a_group_is_allowed_and_exports_nothing() -> None:
    first, second = side("ex/first", group="ex/either"), side("ex/second", group="ex/either")

    found = side_set(first, second).compute(sides(first, 0), sides(second, 0))

    assert grand(found) == D(0)
    (worksheet,) = found[RETURN]
    assert values(worksheet, RecordListKind("ex/first.profit", fields=(PROFIT,))) == []
    assert found["ex/first"] == ()
    assert found["ex/second"] == ()


def test_a_group_of_three_allows_one_form_with_instances() -> None:
    a, b, c = (side(f"ex/{n}", group="ex/any") for n in "abc")

    assert run_sides((a, 0), (b, 1), (c, 0), forms=(a, b, c)) == D(0)
    with pytest.raises(
        ValidationError,
        match=r"^forms 'ex/b' and 'ex/c' both have instances, but are in exclusive group 'ex/any'$",
    ):
        side_set(a, b, c).compute(sides(a, 0), sides(b, 1), sides(c, 1))


def test_two_groups_are_independent() -> None:
    a1, a2 = side("ex/a1", group="ex/left"), side("ex/a2", group="ex/left")
    b1, b2 = side("ex/b1", group="ex/right"), side("ex/b2", group="ex/right")
    both = side_set(a1, a2, b1, b2)

    found = both.compute(sides(a1, 1), sides(a2, 0), sides(b1, 0), sides(b2, 1))
    assert grand(found) == D(6)
    with pytest.raises(
        ValidationError,
        match=(
            r"^forms 'ex/b1' and 'ex/b2' both have instances, "
            "but are in exclusive group 'ex/right'$"
        ),
    ):
        both.compute(sides(a1, 1), sides(a2, 0), sides(b1, 1), sides(b2, 1))


def test_a_form_outside_every_group_is_free_beside_a_group() -> None:
    first, second = side("ex/first", group="ex/either"), side("ex/second", group="ex/either")
    free = side("ex/free")

    assert run_sides((first, 1), (second, 0), (free, 3), forms=(first, second, free)) == D(6)


def test_a_group_naming_one_form_is_refused_when_the_set_is_built() -> None:
    with pytest.raises(
        InvalidCompositionError, match=r"^exclusive group 'ex/alone' names only form 'ex/shop'$"
    ):
        flat(
            [RecordTotal(SHOP_PROFIT, GRAND)],
            inputs=frozenset({SHOPS}),
            outputs=frozenset({GRAND}),
            forms=[
                FormComposition(
                    "ex/shop",
                    [Subtract(SALES, COSTS, PROFIT)],
                    instances=SHOPS,
                    exports=[PROFIT],
                    exclusive_group="ex/alone",
                )
            ],
        )


def test_the_limits_are_checked_after_the_instances_are_all_given() -> None:
    only = side("ex/only", maximum=1)

    with pytest.raises(InvalidCompositionError, match="missing input"):
        side_set(only).compute()


# --- a form reading its own export: the records of its earlier runs ------------------------------

AMOUNT = ArtifactKind("ex/amount", Decimal)
CARRIED = ArtifactKind("ex/carried", Decimal)
STEP_TOTAL = ArtifactKind("ex/total", Decimal)
CHECKED = ArtifactKind("ex/checked", Decimal)
STEPS = RecordListKind("ex/steps", fields=(AMOUNT,))
STEP_TOTALS = RecordListKind("ex/step.total", fields=(STEP_TOTAL,))
EARLY_TOTALS = RecordListKind("ex/early.total", fields=(STEP_TOTAL,))
STEP_RETURN = RecordTotal(STEP_TOTALS, GRAND)


def step(name: str = "ex/step") -> FormComposition:
    """Each step: the amount plus the total carried from the earlier steps' own totals."""
    own = FormComposition.derive(name, [STEP_TOTAL])[0]
    return FormComposition(
        name,
        [RecordTotal(own, CARRIED), Sum((AMOUNT, CARRIED), STEP_TOTAL)],
        instances=STEPS,
        exports=[STEP_TOTAL],
    )


def step_set(*forms: FormComposition) -> FormSet:
    return flat(
        [STEP_RETURN],
        inputs=frozenset({STEPS} | {form.instances for form in forms if form.instances}),
        outputs=frozenset({GRAND}),
        forms=forms,
    )


def steps(*amounts: str) -> Artifact[Any]:
    return Artifact(STEPS, RecordList(STEPS.fields, [{AMOUNT: D(a)} for a in amounts]))


def test_a_form_reading_its_own_export_is_not_a_cycle() -> None:
    assert [form.name for form in step_set(step()).forms] == ["ex/step", RETURN]


def test_a_capability_over_the_form_s_own_export_gives_the_running_total_of_earlier_runs() -> None:
    result = step_set(step()).compute(steps("10", "15", "20"))

    assert [w.get(CARRIED).value for w in result["ex/step"]] == [D(0), D(10), D(35)]
    assert [w.get(STEP_TOTAL).value for w in result["ex/step"]] == [D(10), D(25), D(55)]


def test_run_k_receives_the_own_export_of_the_k_minus_1_earlier_runs_in_order() -> None:
    result = step_set(step()).compute(steps("10", "15", "20"))

    seen = [values(worksheet, STEP_TOTALS) for worksheet in result["ex/step"]]
    assert seen == [[], [D(10)], [D(10), D(25)]]


def test_the_own_export_reaches_the_run_as_a_starting_artifact() -> None:
    result = step_set(step()).compute(steps("10", "15"))

    assert result["ex/step"][1].producer_of(STEP_TOTALS) is None


def test_the_own_export_is_a_record_list_of_the_one_field() -> None:
    result = step_set(step()).compute(steps("10", "15"))

    assert result["ex/step"][1].get(STEP_TOTALS).value == RecordList(
        (STEP_TOTAL,), [{STEP_TOTAL: D(10)}]
    )


def test_the_first_run_of_a_form_reading_its_own_export_sees_an_empty_list() -> None:
    result = step_set(step()).compute(steps("10"))

    assert values(result["ex/step"][0], STEP_TOTALS) == []
    assert result["ex/step"][0].get(CARRIED).value == D(0)


def test_a_form_without_an_instances_list_reading_its_own_export_sees_an_empty_list() -> None:
    once = FormComposition(
        "ex/step",
        [RecordTotal(STEP_TOTALS, CARRIED), Sum((AMOUNT, CARRIED), STEP_TOTAL)],
        exports=[STEP_TOTAL],
        starting=frozenset({AMOUNT}),
    )
    forms = flat(
        [STEP_RETURN],
        inputs=frozenset({AMOUNT}),
        outputs=frozenset({GRAND}),
        forms=[once],
    )

    result = forms.compute(Artifact(AMOUNT, D(7)))

    (only,) = result["ex/step"]
    assert values(only, STEP_TOTALS) == []
    assert only.get(STEP_TOTAL).value == D(7)


def test_each_form_sees_only_its_own_earlier_runs() -> None:
    result = step_set(step(), step("ex/zzz")).compute(steps("10", "15", "20"))

    assert [w.get(STEP_TOTAL).value for w in result["ex/zzz"]] == [D(10), D(25), D(55)]
    assert values(result["ex/zzz"][2], FormComposition.derive("ex/zzz", [STEP_TOTAL])[0]) == [
        D(10),
        D(25),
    ]


def test_later_consumers_see_the_values_the_runs_were_given_as_earlier_runs() -> None:
    forms = step_set(step())
    result = forms.compute(steps("10", "15", "20"))

    final = values(result[RETURN][0], STEP_TOTALS)
    assert final == [D(10), D(25), D(55)]
    for position, worksheet in enumerate(result["ex/step"]):
        assert values(worksheet, STEP_TOTALS) == final[:position]
    assert result[RETURN][0].get(GRAND).value == D(90)


def test_a_form_reading_its_own_export_still_runs_after_the_form_it_imports_from() -> None:
    early = FormComposition(
        "ex/early",
        [
            RecordTotal(EARLY_TOTALS, CARRIED),
            RecordTotal(SHOP_PROFIT, PROFIT_TOTAL),
            Sum((AMOUNT, CARRIED, PROFIT_TOTAL), STEP_TOTAL),
        ],
        instances=STEPS,
        exports=[STEP_TOTAL],
    )

    forms = flat(
        [RecordTotal(EARLY_TOTALS, GRAND)],
        inputs=frozenset({STEPS, SHOPS}),
        outputs=frozenset({GRAND}),
        forms=[early, shop()],
    )

    assert [form.name for form in forms.forms] == ["ex/shop", "ex/early", RETURN]


def test_a_form_reading_its_own_export_still_runs_before_the_forms_that_import_it() -> None:
    late = FormComposition(
        "ex/aaa",
        [RecordTotal(STEP_TOTALS, PROFIT_TOTAL), Sum((FEE, PROFIT_TOTAL), FEE_TOTAL)],
        instances=AUDITS,
        exports=[FEE_TOTAL],
    )
    forms = flat(
        [RecordTotal(FormComposition.derive("ex/aaa", [FEE_TOTAL])[0], GRAND)],
        inputs=frozenset({STEPS, AUDITS}),
        outputs=frozenset({GRAND}),
        forms=[late, step()],
    )

    assert [form.name for form in forms.forms] == ["ex/step", "ex/aaa", RETURN]


def test_a_cycle_between_two_forms_is_still_refused_when_one_reads_its_own_export() -> None:
    reading_shop = FormComposition(
        "ex/shop",
        [
            Subtract(SALES, COSTS, PROFIT),
            RecordTotal(AUDIT_AUDITED, FEE_TOTAL),
            RecordTotal(SHOP_PROFIT, PROFIT_TOTAL),
            Sum((PROFIT_TOTAL, FEE_TOTAL), GRAND),
        ],
        instances=SHOPS,
        exports=[PROFIT, GRAND],
    )

    with pytest.raises(InvalidCompositionError, match="cycle") as caught:
        form_set(reading_shop, audit(), shop("ex/bystander"))

    assert "ex/shop" in str(caught.value) and "ex/audit" in str(caught.value)
    assert "ex/bystander" not in str(caught.value)


def test_a_cycle_through_a_form_that_reads_its_own_export_names_the_forms_on_it() -> None:
    # step reads its own total and ex/back.fee_total; back reads step.total.
    reading = FormComposition(
        "ex/step",
        [
            RecordTotal(STEP_TOTALS, CARRIED),
            RecordTotal(FormComposition.derive("ex/back", [FEE_TOTAL])[0], GRAND),
            Sum((AMOUNT, CARRIED, GRAND), STEP_TOTAL),
        ],
        instances=STEPS,
        exports=[STEP_TOTAL],
    )
    back = FormComposition(
        "ex/back",
        [RecordTotal(STEP_TOTALS, PROFIT_TOTAL), Sum((FEE, PROFIT_TOTAL), FEE_TOTAL)],
        instances=AUDITS,
        exports=[FEE_TOTAL],
    )

    with pytest.raises(InvalidCompositionError, match="cycle") as caught:
        flat(
            [STEP_RETURN],
            inputs=frozenset({STEPS, AUDITS}),
            outputs=frozenset({GRAND}),
            forms=[reading, back],
        )

    assert "ex/step" in str(caught.value) and "ex/back" in str(caught.value)


def test_reading_an_export_the_form_does_not_have_is_still_refused_as_exported_by_no_form() -> None:
    missing = FormComposition(
        "ex/step",
        [
            RecordTotal(RecordListKind("ex/step.nothing", fields=(AMOUNT,)), CARRIED),
            Sum((AMOUNT, CARRIED), STEP_TOTAL),
        ],
        instances=STEPS,
        exports=[STEP_TOTAL],
    )

    with pytest.raises(InvalidCompositionError, match=r"'ex/step': no form exports"):
        step_set(missing)


def test_a_failing_run_of_a_form_reading_its_own_export_names_the_form_and_instance() -> None:
    checked = FormComposition(
        "ex/step",
        [
            Reject(AMOUNT, CHECKED),
            RecordTotal(STEP_TOTALS, CARRIED),
            Sum((CHECKED, CARRIED), STEP_TOTAL),
        ],
        instances=STEPS,
        exports=[STEP_TOTAL],
    )

    with pytest.raises(DomainError, match=r"^ex/step, instance 2: 666 is not accepted$"):
        step_set(checked).compute(steps("10", "666", "20"))


def test_the_trace_names_are_those_of_any_form() -> None:
    forms = step_set(step())
    result = forms.compute(steps("10", "15", "20"))

    lines = instance_lines(forms.trace(result))

    assert [(line.form, line.position) for line in lines] == [
        ("ex/step", 1),
        ("ex/step", 2),
        ("ex/step", 3),
        (RETURN, 1),
    ]
    assert lines[2].lines == result["ex/step"][2].trace
    assert [type(line) for line in lines[2].lines] == [RecordTotalLine, type(lines[2].lines[1])]


def test_a_form_set_refuses_a_blank_starting_artifact() -> None:
    forms = flat(
        [Subtract(SALES, COSTS, LEVY)], inputs=frozenset({SALES, COSTS}), outputs=frozenset({LEVY})
    )

    with pytest.raises(BlankNotAllowedError, match="'sales' may not be left blank"):
        forms.compute(Artifact(SALES, BLANK), Artifact(COSTS, Decimal(1)))


# --- inputs the caller leaves out take their manifest default --------------------------------


class Less(Capability):
    """`target` = `source` less `cost`; a blank `cost` is read as the rule says, a blank `source`
    is refused.
    """

    CONSUMES: ClassVar[Mapping[str, type]] = {"source": Decimal, "cost": Decimal}
    PRODUCES: ClassVar[Mapping[str, type]] = {"target": Decimal}
    BLANK_ALLOWED: ClassVar[frozenset[str]] = frozenset({"cost"})

    def __init__(
        self, source: ArtifactKind[Decimal], cost: ArtifactKind[Decimal], target: ArtifactKind[Any]
    ) -> None:
        super().__init__(source=source, cost=cost, target=target)
        self._source, self._cost, self._target = source, cost, target

    def compute(self, inputs: tuple[Artifact[Any], ...]) -> CapabilityResult:
        value = self._input(inputs, self._source).value - self._input(inputs, self._cost).value
        return CapabilityResult(outputs=(Artifact(self._target, value),), trace=())


def less_form(*, blank_inputs: frozenset[ArtifactKind[Any]]) -> FormComposition:
    return FormComposition(
        RETURN,
        [Less(SALES, COSTS, LEVY).with_blank_rules({"cost": D(0)})],
        exports=[LEVY],
        starting=frozenset({SALES, COSTS}),
        blank_inputs=blank_inputs,
    )


def less_set(
    defaults: Iterable[Artifact[Any]], *, blank_inputs: frozenset[ArtifactKind[Any]] = frozenset()
) -> FormSet:
    return FormSet(
        [less_form(blank_inputs=blank_inputs)],
        inputs=frozenset({SALES, COSTS}),
        defaults=defaults,
    )


def levy(forms: FormSet, *given: Artifact[Any]) -> Decimal:
    return forms.compute(*given)[RETURN][0].get(LEVY).value


def test_an_input_the_caller_leaves_out_takes_its_default() -> None:
    forms = less_set([Artifact(COSTS, D(30))])

    assert levy(forms, Artifact(SALES, D(100))) == D(70)


def test_an_input_the_caller_gives_beats_its_default() -> None:
    forms = less_set([Artifact(COSTS, D(30))])

    assert levy(forms, Artifact(SALES, D(100)), Artifact(COSTS, D(10))) == D(90)


def test_a_required_input_left_out_is_refused_naming_it() -> None:
    forms = less_set([Artifact(COSTS, D(30))])

    with pytest.raises(InvalidCompositionError, match="missing input 'sales'"):
        forms.compute(Artifact(COSTS, D(1)))


def test_a_default_blank_reaches_the_form_that_declares_it_and_its_own_rule_applies() -> None:
    forms = less_set([Artifact(COSTS, BLANK)], blank_inputs=frozenset({COSTS}))

    assert levy(forms, Artifact(SALES, D(100))) == D(100)


def test_a_blank_the_caller_gives_for_an_input_with_a_value_default_is_read_as_the_default() -> (
    None
):
    forms = less_set([Artifact(COSTS, D(30))])

    assert levy(forms, Artifact(SALES, D(100)), Artifact(COSTS, BLANK)) == D(70)


def test_a_blank_the_caller_gives_for_a_blank_default_stays_blank_for_the_forms_rule() -> None:
    forms = less_set([Artifact(COSTS, BLANK)], blank_inputs=frozenset({COSTS}))

    assert levy(forms, Artifact(SALES, D(100)), Artifact(COSTS, BLANK)) == D(100)


def test_a_form_that_does_not_declare_the_blank_input_refuses_it() -> None:
    forms = less_set([Artifact(COSTS, BLANK)])

    with pytest.raises(BlankNotAllowedError, match=r"ex-on/return, instance 1: 'costs' may not"):
        forms.compute(Artifact(SALES, D(100)))


def test_each_form_has_its_own_blank_inputs() -> None:
    open_form = less_form(blank_inputs=frozenset({COSTS}))
    strict_form = FormComposition(
        "ex/strict",
        [Subtract(SALES, COSTS, PROFIT)],
        exports=[PROFIT],
        starting=frozenset({SALES, COSTS}),
    )
    forms = FormSet(
        [open_form, strict_form],
        inputs=frozenset({SALES, COSTS}),
        defaults=[Artifact(COSTS, BLANK)],
    )

    with pytest.raises(BlankNotAllowedError, match=r"^ex/strict, instance 1: 'costs'"):
        forms.compute(Artifact(SALES, D(100)))


def test_a_blank_the_form_does_not_read_is_not_its_to_refuse() -> None:
    reads_sales_only = FormComposition(
        RETURN, [Reject(SALES, LEVY)], exports=[LEVY], starting=frozenset({SALES})
    )
    other = FormComposition(
        "ex/other",
        [Less(SALES, COSTS, PROFIT).with_blank_rules({"cost": D(0)})],
        exports=[PROFIT],
        starting=frozenset({SALES, COSTS}),
        blank_inputs=frozenset({COSTS}),
    )
    forms = FormSet(
        [reads_sales_only, other],
        inputs=frozenset({SALES, COSTS}),
        defaults=[Artifact(COSTS, BLANK)],
    )

    assert levy(forms, Artifact(SALES, D(100))) == D(100)


def test_a_blank_instances_list_is_refused_naming_it_before_any_form_runs() -> None:
    forms = form_set(shop(), audit())
    audits_blank = Artifact(AUDITS, BLANK)

    with pytest.raises(BlankNotAllowedError, match="'audits' may not be left blank"):
        forms.compute(TWO_SHOPS, audits_blank)


def test_a_default_instances_list_is_an_empty_list() -> None:
    empty = Artifact(SHOPS, RecordList(SHOPS.fields, ()))
    forms = FormSet(
        [shop(), audit()],
        inputs=frozenset({SHOPS, AUDITS}),
        defaults=[empty],
    )

    result = forms.compute(TWO_AUDITS)

    assert result["ex/shop"] == ()
    assert len(result["ex/audit"]) == 2


def test_a_default_for_a_kind_that_is_not_an_input_is_refused() -> None:
    with pytest.raises(InvalidCompositionError, match="default for 'fee', which is not an input"):
        less_set([Artifact(FEE, D(1))])


def test_two_defaults_for_one_kind_are_refused() -> None:
    with pytest.raises(InvalidCompositionError, match="two defaults for 'costs'"):
        less_set([Artifact(COSTS, D(1)), Artifact(COSTS, BLANK)])


def test_a_form_that_exports_a_blank_input_is_refused_naming_the_form_and_instance() -> None:
    fact = FormComposition(
        "ex/fact", [], exports=[FEE], starting=frozenset({FEE}), blank_inputs=frozenset({FEE})
    )
    forms = FormSet([fact], inputs=frozenset({FEE}), defaults=[Artifact(FEE, BLANK)])

    with pytest.raises(BlankNotAllowedError, match=r"^ex/fact, instance 1: 'fee' is blank"):
        forms.compute()


def test_a_blank_instances_list_with_an_empty_list_default_is_read_as_no_instances() -> None:
    empty = Artifact(SHOPS, RecordList(SHOPS.fields, ()))
    forms = FormSet([shop(), audit()], inputs=frozenset({SHOPS, AUDITS}), defaults=[empty])

    result = forms.compute(Artifact(SHOPS, BLANK), TWO_AUDITS)

    assert result["ex/shop"] == ()
