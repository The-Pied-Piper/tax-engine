"""YamlJurisdictionSource: an input belongs to the form that declares it.

A part with a `form:` key gives its `inputs` to that form, a part without one (or a whole-file
manifest) gives them to the default form, and the parts of an imported form give theirs to the
imported form. A form's composition starts from its own inputs only, so every other form reads the
owner's export instead, and a step that reads another form's input fails when the forms are
composed, naming the form and the input. Names are made up: `ex/federal` is imported by `ex-on`,
whose own forms are the default `ex-on/return` and `ex-on/levy`.
"""

from __future__ import annotations

from pathlib import Path

from tax_engine.adapters.outbound.yaml_parameters import YamlParameterSource
from tax_engine.application.services.tax_computation import TaxComputationService
from tax_engine.domain.capability import CapabilityRegistry
from tax_engine.domain.manifest import Manifest
from tax_engine.jurisdictions.core.capabilities.record_total import RecordTotal
from tax_engine.registrations import parameter_parsers
from tests.adapters.outbound.test_yaml_imports import (
    EX_ON,
    FEDERAL,
    FEDERAL_INPUTS,
    FEDERAL_STANDALONE,
    Half,
    header,
    manifest_of,
    package_roots,
    province_form,
    source,
    write_federal,
    write_province,
)
from tests.adapters.outbound.test_yaml_jurisdictions import write
from tests.application.services.test_every_resolvable_year import composition_failures

LEVY_INPUT = "ex-on/levy"
RETURN = "ex-on/return"


def composing(directory: Path) -> TaxComputationService:
    capabilities = CapabilityRegistry()
    capabilities.register("core/record_total", RecordTotal)
    capabilities.register("ex/half", Half)
    parameters = YamlParameterSource(package_roots(directory), parameter_parsers())
    return TaxComputationService(source(directory), parameters, capabilities)


def owner_of(manifest: Manifest, name: str) -> str:
    """The name of the one form of `manifest` that declares the input `name`."""
    (owner,) = (form.name for form in manifest.forms if name in {i.name for i in form.inputs})
    return owner


def test_an_input_in_a_part_with_a_form_key_belongs_to_that_form(tmp_path: Path) -> None:
    write_federal(tmp_path)
    write_province(tmp_path)

    assert owner_of(manifest_of(tmp_path), "ex/income") == LEVY_INPUT


def test_an_input_in_a_part_without_a_form_key_belongs_to_the_default_form(
    tmp_path: Path,
) -> None:
    write_federal(tmp_path)
    write_province(tmp_path)
    plain = "inputs: [{name: ex/note, required: false, default: '', basis: b}]\n"
    write(tmp_path, "ex-on/manifests/v1/02-note.yaml", plain)

    assert owner_of(manifest_of(tmp_path), "ex/note") == RETURN


def test_an_input_in_a_whole_file_manifest_belongs_to_the_default_form(tmp_path: Path) -> None:
    write_federal(tmp_path, {"00-federal.yaml": FEDERAL_STANDALONE})
    write(tmp_path, "ex-on/manifests/v1.yaml", header("EX-ON", inputs=True) + "capabilities: []\n")

    assert owner_of(manifest_of(tmp_path), "ex/income") == RETURN


def test_an_input_an_imported_form_declares_belongs_to_the_imported_form(tmp_path: Path) -> None:
    write_federal(tmp_path, {"00-federal.yaml": FEDERAL, "01-inputs.yaml": FEDERAL_INPUTS})
    write_province(tmp_path)

    assert owner_of(manifest_of(tmp_path), "ex/other_income") == "ex/federal"


def test_a_step_reading_an_input_another_form_owns_does_not_compose(tmp_path: Path) -> None:
    write_federal(tmp_path, {"00-federal.yaml": FEDERAL, "01-inputs.yaml": FEDERAL_INPUTS})
    reads_federal_input = province_form("ex-on").replace(
        "source: ex/income", "source: ex/other_income"
    )
    write_province(tmp_path, form=reads_federal_input)

    failures = composition_failures(composing(tmp_path), EX_ON, [2025])

    assert len(failures) == 1
    assert "other_income" in failures[0]


def test_a_step_reading_its_own_input_and_another_forms_export_loads(tmp_path: Path) -> None:
    write_federal(tmp_path)
    write_province(tmp_path)

    reading_both = manifest_of(tmp_path)

    federal = next(form for form in reading_both.forms if form.name == "ex/federal")
    assert federal.capabilities[0].consumes == {"records": "ex/provincial_tax.amount"}
    assert owner_of(reading_both, "ex/income") == LEVY_INPUT
