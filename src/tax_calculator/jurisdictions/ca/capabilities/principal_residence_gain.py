"""PrincipalResidenceGain: the gain left after the principal residence exemption, one property each.

For Form T2091(IND) Part 1, Part 2 and Part 3, completed for each property sold: Part 1 is the
`PrincipalResidenceRows` base's: the proceeds (line 8) less the adjusted cost base (line 10) and the
outlays (line 9) is the gain (line 18); the years designated after 1981 and from 1972 to 1981 (lines
1 and 2) added to the "plus one" year when it applies (line 20) multiply the gain (line 21), which
is divided by the years owned (line 7, the sum of lines 5 and 6) to give the exempt part (line 23);
and the gain less that, from 0, is line 24. Part 2 (lines 27 to 53) applies to a property that is
one of two or more principal residences a family member owned on December 31, 1981, and is worked by
the `principal_residence_line_N` capabilities. Line 54 is the lesser of line 53 and line 24 when
Part 2 applies, else line 24 (Part 3). The figures of each property are fields of each record in the
consumed record list. The output is the total of those amounts (line 54), 0 when there are no
properties. Each property is worked on its own, never pooled with the others, and line 23 is the
exact fraction rounded once, with the `rounding` dataset's rule, before it is taken off; the other
lines stay exact. A property owned for no years is refused, line 22 being the divisor. It records
one `PrincipalResidenceGainLine` for each property, by position from 1, then an `ItemsTotalLine`.
"""

from __future__ import annotations

from collections.abc import Mapping
from decimal import Decimal
from typing import Any, ClassVar

from tax_calculator.domain.artifact import Artifact, ArtifactKind, Money
from tax_calculator.domain.capability import CapabilityResult, capability
from tax_calculator.domain.parameters.datasets import ParameterDataset
from tax_calculator.domain.parameters.rounding_only import RoundingOnly
from tax_calculator.domain.record_list import RecordList
from tax_calculator.jurisdictions.ca.capabilities.principal_residence_rows import PrincipalResidenceRows
from tax_calculator.jurisdictions.ca.trace import PrincipalResidenceGainLine


@capability(identifier="principal_residence_gain")
class PrincipalResidenceGain(PrincipalResidenceRows):
    """Produces `output`: the total, over the consumed `properties`, of each one's line 54: the
    gain less its principal residence exemption, from 0, or the lesser of its Part 2 net capital
    gain and that gain when Part 2 applies."""

    PRODUCES: ClassVar[Mapping[str, type]] = {"output": Decimal}

    def __init__(
        self,
        rounding: ParameterDataset[RoundingOnly],
        properties: ArtifactKind[RecordList],
        output: Money,
    ) -> None:
        """Wire the capability: its rounding dataset, the record list read, the kind produced."""
        super().__init__(rounding, properties, output)
        self._output = output

    def compute(self, inputs: tuple[Artifact[Any], ...]) -> CapabilityResult:
        return self._result(
            [
                PrincipalResidenceGainLine(
                    self._output,
                    row.position,
                    row.designated_after,
                    row.designated_before,
                    row.designated,
                    row.owned_after,
                    row.owned_before,
                    row.owned,
                    row.plus_one,
                    row.proceeds,
                    row.adjusted_cost_base,
                    row.outlays,
                    row.gain,
                    row.line_20,
                    row.line_21,
                    row.rounding,
                    row.exempt,
                    row.part_2_applies,
                    row.line_53,
                    row.line_24,
                    row.line_54,
                )
                for row in self._rows(inputs)
            ]
        )
