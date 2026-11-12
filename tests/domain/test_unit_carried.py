"""Units carried as data: on the artifact, the worksheet, the form composition and the trace.

A manifest names a unit for an input, a field or the figure a selection produces. The unit is then
readable as data, without rendering English: `Artifact.unit` (None when the figure has none),
`Worksheet.unit(label)`, `Worksheet.unit_of(line)` for a trace line's figure, and
`FormComposition.figure_units`. An artifact's producer and its consumers may not disagree on its
unit. Names and units are made up.
"""

from __future__ import annotations

from decimal import Decimal

import pytest

from tax_engine.domain.artifact import Artifact
from tax_engine.domain.errors import InvalidCompositionError, InvalidManifestError
from tax_engine.domain.figure_names import ImportedFigure
from tax_engine.domain.form import FormComposition, FormSet
from tax_engine.domain.kinds import AmountKind, CountKind, RecordListKind
from tax_engine.domain.manifest import CapabilitySelection, InputDeclaration
from tax_engine.domain.parameters.datasets import ParameterDataset
from tax_engine.domain.parameters.rounding import NO_ROUNDING
from tax_engine.domain.parameters.rounding_only import ROUNDING_ONLY, RoundingOnly
from tax_engine.domain.trace import DefaultedInputLine
from tax_engine.domain.unit import Unit
from tax_engine.domain.worksheet import Worksheet
from tax_engine.jurisdictions.core.capabilities.subtract import Subtract
from tests.forms import composition

D = Decimal

CROWNS = Unit("ex/crowns")
MOONS = Unit("ex/moons")
UNITS = {"ex/crowns": CROWNS, "ex/moons": MOONS}

EXACT = ParameterDataset(
    "ex/rounding", 2025, ROUNDING_ONLY, RoundingOnly(), NO_ROUNDING, ("https://example.org/r",)
)
INCOME = AmountKind("ex/income")
RELIEF = AmountKind("ex/relief")
NET = AmountKind("ex/net")
TERM = CountKind("ex/term")


def test_an_artifact_has_no_unit_by_default() -> None:
    assert Artifact(INCOME, D("1")).unit is None
    assert Artifact(TERM, 12).unit is None


def test_an_artifact_may_carry_a_unit() -> None:
    artifact = Artifact(TERM, 12, unit=MOONS)

    assert artifact.unit is MOONS
    assert artifact.value == 12


def test_a_blank_artifact_may_carry_a_unit_too() -> None:
    from tax_engine.domain.blank import BLANK

    assert Artifact(INCOME, BLANK, unit=CROWNS).unit is CROWNS


def test_the_unit_is_not_part_of_the_kind_or_the_value() -> None:
    assert Artifact(INCOME, D("1")).value == Artifact(INCOME, D("1"), unit=CROWNS).value
    assert Artifact(INCOME, D("1"), unit=CROWNS).kind == INCOME


def test_a_selection_and_an_input_have_no_unit_by_default() -> None:
    assert InputDeclaration("ex/income", True).unit is None
    assert CapabilitySelection("ex/a", {}, {}, {"output": "ex/net"}).unit is None


def test_a_selection_unit_belongs_to_the_one_figure_it_produces() -> None:
    with pytest.raises(InvalidManifestError, match="unit belongs to the one figure"):
        CapabilitySelection("ex/a", {}, {}, {"output": "ex/net", "other": "ex/x"}, unit="ex/crowns")


def test_a_worksheet_reads_the_unit_of_a_figure_by_label() -> None:
    sheet = Worksheet(figure_units={"income": CROWNS})

    assert sheet.unit("income") is CROWNS
    assert sheet.unit("relief") is None


def test_a_starting_artifact_carries_the_unit_its_worksheet_gives_its_figure() -> None:
    sheet = Worksheet(Artifact(INCOME, D("70000")), figure_units={"income": CROWNS})

    assert sheet.get(INCOME).unit is CROWNS


def test_a_starting_artifact_without_a_unit_stays_without() -> None:
    sheet = Worksheet(Artifact(INCOME, D("70000")), figure_units={"net": CROWNS})

    assert sheet.get(INCOME).unit is None


def test_a_produced_artifact_carries_the_unit_of_its_figure() -> None:
    sheet = Worksheet(
        Artifact(INCOME, D("1000")),
        Artifact(RELIEF, D("400")),
        figure_units={"income": CROWNS, "relief": CROWNS, "net": CROWNS},
    )

    sheet.apply(Subtract(EXACT, INCOME, RELIEF, NET))

    assert sheet.get(NET).value == D("600")
    assert sheet.get(NET).unit is CROWNS


def test_a_produced_artifact_of_a_figure_with_no_unit_has_none() -> None:
    sheet = Worksheet(Artifact(INCOME, D("1000")), Artifact(RELIEF, D("400")))

    sheet.apply(Subtract(EXACT, INCOME, RELIEF, NET))

    assert sheet.get(NET).unit is None


def test_the_unit_of_a_trace_lines_figure_is_readable_without_rendering() -> None:
    sheet = Worksheet(
        Artifact(INCOME, D("1000")),
        Artifact(RELIEF, D("400")),
        figure_units={"net": CROWNS},
    )
    sheet.apply(Subtract(EXACT, INCOME, RELIEF, NET))

    (line,) = sheet.trace

    assert line.label == "net"
    assert sheet.unit_of(line) is CROWNS


def test_the_unit_of_a_trace_line_about_no_figure_or_an_unitless_one_is_none() -> None:
    sheet = Worksheet(Artifact(INCOME, D("1000")), Artifact(RELIEF, D("400")))
    sheet.apply(Subtract(EXACT, INCOME, RELIEF, NET))
    (line,) = sheet.trace

    assert sheet.unit_of(line) is None


def test_a_defaulted_inputs_trace_line_has_the_unit_of_its_figure() -> None:
    sheet = Worksheet(
        Artifact(TERM, 12),
        defaulted=[TERM],
        figure_units={"term": MOONS},
    )
    (line,) = sheet.trace

    assert sheet.unit_of(line) is MOONS
    assert sheet.get(TERM).unit is MOONS


def test_a_form_composition_has_no_figure_units_unless_its_manifest_names_some() -> None:
    form = composition(
        "ex-on/levy",
        [Subtract(EXACT, INCOME, RELIEF, NET)],
        exports=[NET],
        starting=frozenset({INCOME, RELIEF}),
    )

    assert dict(form.figure_units) == {}


def test_a_form_composition_collects_the_units_of_its_inputs_and_its_steps_by_label() -> None:
    form = composition(
        "ex-on/levy",
        [Subtract(EXACT, INCOME, RELIEF, NET)],
        exports=[NET],
        starting=frozenset({INCOME, RELIEF}),
        selections=(
            CapabilitySelection(
                "core/subtract",
                {},
                {"minuend": "ex/income", "subtrahend": "ex/relief"},
                {"output": "ex/net"},
                unit="ex/moons",
            ),
        ),
        declared=(
            InputDeclaration("ex/income", True, unit="ex/moons"),
            InputDeclaration("ex/relief", True),
        ),
        units=UNITS,
    )

    assert dict(form.figure_units) == {"income": MOONS, "net": MOONS}


def test_the_form_hands_its_units_to_each_worksheet_it_computes() -> None:
    form = composition(
        "ex-on/levy",
        [Subtract(EXACT, INCOME, RELIEF, NET)],
        exports=[NET],
        starting=frozenset({INCOME, RELIEF}),
        selections=(
            CapabilitySelection(
                "core/subtract",
                {},
                {"minuend": "ex/income", "subtrahend": "ex/relief"},
                {"output": "ex/net"},
                unit="ex/crowns",
            ),
        ),
        declared=(InputDeclaration("ex/income", True, unit="ex/crowns"),),
        units=UNITS,
    )
    forms = FormSet([form], inputs=frozenset({INCOME, RELIEF}))

    (sheet,) = forms.compute(Artifact(INCOME, D("1000")), Artifact(RELIEF, D("400")))["ex-on/levy"]

    assert sheet.get(INCOME).unit is CROWNS
    assert sheet.get(RELIEF).unit is None
    assert sheet.get(NET).unit is CROWNS
    assert sheet.unit_of(sheet.trace[0]) is CROWNS


def test_the_manifest_decides_a_starting_artifact_passed_with_a_unit_loses_it() -> None:
    sheet = Worksheet(Artifact(INCOME, D("70000"), unit=CROWNS), figure_units={"net": CROWNS})

    assert sheet.get(INCOME).unit is None


def test_the_manifest_decides_a_unit_the_caller_gives_a_figure_with_another_is_replaced() -> None:
    sheet = Worksheet(Artifact(INCOME, D("70000"), unit=MOONS), figure_units={"income": CROWNS})

    assert sheet.get(INCOME).unit is CROWNS


def test_a_form_without_a_unit_for_a_figure_strips_the_unit_of_the_artifact_passed_in() -> None:
    form = composition(
        "ex-on/levy",
        [Subtract(EXACT, INCOME, RELIEF, NET)],
        exports=[NET],
        starting=frozenset({INCOME, RELIEF}),
        selections=(
            CapabilitySelection(
                "core/subtract",
                {},
                {"minuend": "ex/income", "subtrahend": "ex/relief"},
                {"output": "ex/net"},
            ),
        ),
        units=UNITS,
    )
    forms = FormSet([form], inputs=frozenset({INCOME, RELIEF}))

    (sheet,) = forms.compute(
        Artifact(INCOME, D("1000"), unit=CROWNS), Artifact(RELIEF, D("400"), unit=MOONS)
    )["ex-on/levy"]

    assert sheet.get(INCOME).unit is None
    assert sheet.get(RELIEF).unit is None
    assert sheet.get(NET).unit is None


def test_an_imported_figure_has_the_unit_of_its_exporter() -> None:
    sheet = Worksheet(imported_figures={"income": ImportedFigure(None, None, "4", False, CROWNS)})

    assert sheet.unit("income") is CROWNS
    assert sheet.unit("relief") is None


def test_the_unit_of_a_trace_line_about_an_imported_figure_is_its_exporters() -> None:
    sheet = Worksheet(
        Artifact(INCOME, D("1000")),
        defaulted=[INCOME],
        imported_figures={"income": ImportedFigure(None, None, "4", False, CROWNS)},
    )
    (line,) = sheet.trace

    assert isinstance(line, DefaultedInputLine)
    assert sheet.unit_of(line) is CROWNS


def test_a_worksheets_own_unit_for_a_figure_comes_before_the_imported_one() -> None:
    sheet = Worksheet(
        figure_units={"income": MOONS},
        imported_figures={"income": ImportedFigure(None, None, None, False, CROWNS)},
    )

    assert sheet.unit("income") is MOONS


def test_an_imported_figure_with_no_unit_has_none() -> None:
    sheet = Worksheet(imported_figures={"income": ImportedFigure(None, None, None, False)})

    assert sheet.unit("income") is None


# One record list, one field: the consumers and a producer of the field `ex/fee`.
FEE = AmountKind("ex/fee")
FEE2 = AmountKind("ex/fee_less")
AUDITS = RecordListKind("ex/audits", fields=(FEE, FEE2))
FEE_TOTAL = AmountKind("ex/fee_total")
OTHER_TOTAL = AmountKind("ex/other_total")


def reader(name: str, total: AmountKind, unit: str | None) -> FormComposition:
    return composition(
        name,
        [Subtract(EXACT, FEE, FEE2, total)],
        exports=[total],
        instances=AUDITS,
        fields=(
            InputDeclaration("ex/fee", True, unit=unit),
            InputDeclaration("ex/fee_less", True),
        ),
        units=UNITS,
    )


def test_forms_reading_a_field_in_one_unit_agree() -> None:
    first = reader("ex/first", FEE_TOTAL, "ex/crowns")
    second = reader("ex/second", OTHER_TOTAL, "ex/crowns")

    FormSet([first, second], inputs=frozenset({AUDITS}))


def test_two_consumers_disagreeing_on_the_unit_of_a_field_are_refused() -> None:
    first = reader("ex/first", FEE_TOTAL, "ex/crowns")
    second = reader("ex/second", OTHER_TOTAL, "ex/moons")

    with pytest.raises(
        InvalidCompositionError, match=r"'fee'.*'ex/crowns'.*'ex/first'.*'ex/moons'.*'ex/second'"
    ):
        FormSet([first, second], inputs=frozenset({AUDITS}))


def test_a_consumer_with_a_unit_and_one_without_disagree() -> None:
    first = reader("ex/first", FEE_TOTAL, "ex/crowns")
    second = reader("ex/second", OTHER_TOTAL, None)

    with pytest.raises(InvalidCompositionError, match=r"'fee'.*unit"):
        FormSet([first, second], inputs=frozenset({AUDITS}))


def test_a_producer_and_a_consumer_disagreeing_on_the_unit_are_refused() -> None:
    producer = composition(
        "ex/producer",
        [Subtract(EXACT, INCOME, RELIEF, FEE)],
        exports=[FEE],
        starting=frozenset({INCOME, RELIEF}),
        selections=(
            CapabilitySelection(
                "core/subtract",
                {},
                {"minuend": "ex/income", "subtrahend": "ex/relief"},
                {"output": "ex/fee"},
                unit="ex/moons",
            ),
        ),
        units=UNITS,
    )
    consumer = reader("ex/consumer", FEE_TOTAL, "ex/crowns")

    with pytest.raises(
        InvalidCompositionError,
        match=r"'fee'.*produced in 'ex/moons' by 'ex/producer'.*'ex/crowns'.*'ex/consumer'",
    ):
        FormSet(
            [producer, consumer],
            inputs=frozenset({AUDITS, INCOME, RELIEF}),
        )
