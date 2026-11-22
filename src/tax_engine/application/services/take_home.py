"""Take-home pay: the salary less the figures a jurisdiction declares, read off its return.

The service knows no form or figure by name: the jurisdiction's manifest declares where each
figure is read (`TakeHomeFigures`), the computation runs the forms, and the words and unit text
come through a port. The rules (one sheet, one unit, the sums) are the domain's.
"""

from __future__ import annotations

from collections.abc import Mapping, Sequence

from tax_engine.application.models.calculation_request import TaxCalculationRequest
from tax_engine.application.models.take_home import (
    DeductionFigure,
    FormTrace,
    Rate,
    TakeHomeResult,
    TraceEntry,
)
from tax_engine.application.models.take_home_request import TakeHomeRequest
from tax_engine.application.ports.jurisdiction_source import JurisdictionSource
from tax_engine.application.ports.take_home_text import TakeHomeText
from tax_engine.application.services.tax_computation import TaxComputationService
from tax_engine.domain.artifact import Artifact, ArtifactRegistry
from tax_engine.domain.errors import NotFoundError
from tax_engine.domain.take_home import FigureReference, Totals, rate_unit, shared_unit
from tax_engine.domain.trace import TraceLine
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
        figures, and InvalidManifestError when a declared figure is not a decimal, its form has not
        one worksheet, a rate has no unit or the figures taken off do not share one unit.
        """
        who = f"{request.jurisdiction} {request.tax_year}"
        manifest = self._jurisdictions.get_jurisdiction(request.jurisdiction).manifest_for(
            request.tax_year
        )
        declared = manifest.take_home
        if declared is None:
            raise NotFoundError(f"no take-home figures for jurisdiction {who}")
        kinds = manifest.kinds
        salary = Artifact(kinds.kind(declared.salary), request.salary)
        sheets = self._computation.calculate(
            TaxCalculationRequest(request.jurisdiction, request.tax_year, (salary,))
        )
        read = [(name, reference.read(sheets, kinds)) for name, reference in declared.figures]
        unit = shared_unit(who, (value for _, value in read))
        totals = Totals.of(request.salary, ((name, value.amount) for name, value in read))
        return TakeHomeResult(
            salary=totals.salary,
            figures=tuple(DeductionFigure(name, value.amount) for name, value in read),
            total_deductions=totals.total_deductions,
            income_tax=totals.income_tax,
            take_home=totals.take_home,
            unit=self._text.unit(unit),
            average_income_tax_rate=self._rate(
                who, sheets, kinds, declared.average_income_tax_rate
            ),
            marginal_income_tax_rate=self._rate(
                who, sheets, kinds, declared.marginal_income_tax_rate
            ),
            trace=self._trace(sheets) if request.include_trace else None,
        )

    def _rate(
        self,
        who: str,
        sheets: Mapping[str, Sequence[Worksheet]],
        kinds: ArtifactRegistry,
        reference: FigureReference,
    ) -> Rate:
        value = reference.read(sheets, kinds)
        return Rate(value.amount, self._text.unit(rate_unit(who, value)))

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
