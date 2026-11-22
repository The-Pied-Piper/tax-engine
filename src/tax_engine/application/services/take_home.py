"""Take-home pay: the salary less the figures a jurisdiction declares, read off its return.

The service knows no form or figure by name: the jurisdiction's manifest declares where each
figure is read (`TakeHomeFigures`), the computation runs the forms, and the words and unit text
come through a port. The sum and the rounding are the domain's (`TakeHomeResult.of`).
"""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from decimal import Decimal

from tax_engine.application.ports.jurisdiction_source import JurisdictionSource
from tax_engine.application.ports.take_home_text import TakeHomeText
from tax_engine.application.services.tax_computation import TaxComputationService
from tax_engine.domain.artifact import Artifact, ArtifactRegistry
from tax_engine.domain.calculation_request import TaxCalculationRequest
from tax_engine.domain.errors import InvalidManifestError, NotFoundError
from tax_engine.domain.take_home import (
    DeductionFigure,
    FigureReference,
    FormTrace,
    Rate,
    TakeHomeRequest,
    TakeHomeResult,
    TraceEntry,
)
from tax_engine.domain.trace import TraceLine
from tax_engine.domain.unit import Unit
from tax_engine.domain.worksheet import Worksheet


class TakeHomeService:
    """Answers a `TakeHomeRequest` for a jurisdiction that declares its take-home figures."""

    def __init__(
        self,
        jurisdictions: JurisdictionSource,
        computation: TaxComputationService,
        text: TakeHomeText,
    ) -> None:
        """Find declarations in `jurisdictions`, compute with `computation`, word with `text`."""
        self._jurisdictions = jurisdictions
        self._computation = computation
        self._text = text

    def compute(self, request: TakeHomeRequest) -> TakeHomeResult:
        """The take-home answer for `request`.

        Raises NotFoundError when the jurisdiction's manifest for the tax year declares no take-home
        figures, and InvalidManifestError when a declared figure has no unit or the figures do not
        share one.
        """
        manifest = self._jurisdictions.get_jurisdiction(request.jurisdiction).manifest_for(
            request.tax_year
        )
        declared = manifest.take_home
        if declared is None:
            raise NotFoundError(
                f"no take-home figures for jurisdiction {request.jurisdiction} "
                f"in tax year {request.tax_year}"
            )
        kinds = manifest.kinds
        salary = Artifact(kinds.kind(declared.salary), request.salary)
        sheets = self._computation.calculate(
            TaxCalculationRequest(request.jurisdiction, request.tax_year, (salary,))
        )
        figures = tuple(
            DeductionFigure(name, self._read(sheets, kinds, reference)[0])
            for name, reference in declared.figures
        )
        units = {self._read(sheets, kinds, reference)[1] for _, reference in declared.figures}
        if len(units) != 1 or None in units:
            raise InvalidManifestError(
                f"{request.jurisdiction} {request.tax_year}: the figures do not share one unit"
            )
        (unit,) = units
        assert unit is not None
        return TakeHomeResult.of(
            request.salary,
            figures,
            self._text.unit(unit),
            self._rate(sheets, kinds, declared.average_income_tax_rate),
            self._rate(sheets, kinds, declared.marginal_income_tax_rate),
            self._trace(sheets) if request.include_trace else None,
        )

    @staticmethod
    def _read(
        sheets: Mapping[str, Sequence[Worksheet]],
        kinds: ArtifactRegistry,
        reference: FigureReference,
    ) -> tuple[Decimal, Unit | None]:
        (sheet,) = sheets[reference.form]
        artifact = sheet.get(kinds.kind(reference.kind))
        value = artifact.value
        if not isinstance(value, Decimal):
            raise InvalidManifestError(f"{reference.kind} is not a decimal")
        return value, artifact.unit

    def _rate(
        self,
        sheets: Mapping[str, Sequence[Worksheet]],
        kinds: ArtifactRegistry,
        reference: FigureReference,
    ) -> Rate:
        value, unit = self._read(sheets, kinds, reference)
        if unit is None:
            raise InvalidManifestError(f"{reference.kind} has no unit")
        return Rate(value, self._text.unit(unit))

    def _trace(self, sheets: Mapping[str, Sequence[Worksheet]]) -> tuple[FormTrace, ...]:
        return tuple(
            FormTrace(
                form=form,
                name=sheet.form_title or None,
                lines=tuple(self._entry(sheet, line) for line in sheet.trace),
            )
            for form, form_sheets in sheets.items()
            for sheet in form_sheets
        )

    def _entry(self, sheet: Worksheet, line: TraceLine) -> TraceEntry:
        label = line.label
        unit = None if label is None else sheet.unit(label)
        return TraceEntry(
            label=label,
            name=None if label is None else sheet.title(label) or None,
            reference=None if label is None else sheet.reference(label) or None,
            amount=line.amount,
            text=self._text.sentence(line, sheet),
            unit=None if unit is None else self._text.unit(unit),
        )
