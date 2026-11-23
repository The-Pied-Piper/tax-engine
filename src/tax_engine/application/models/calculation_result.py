"""What a tax calculation answers: the worksheets of every form, by form name."""

from __future__ import annotations

from tax_engine.domain.worksheet import Worksheet

type TaxCalculationResult = dict[str, tuple[Worksheet, ...]]
