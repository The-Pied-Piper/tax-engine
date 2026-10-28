"""PrincipalResidenceDesignationBoxCapability: Form 5000-S3 Part 1 line 17900, the principal
residence designation box (1, 2 or 3; 0 with no property), worked from the consumed
`properties` of Form T2091(IND).

Line 17900 "Box 1: I designate the property as my principal residence for all of the years that I
owned it or for all of the years that I owned it except one year. Box 2: I designate the property as
my principal residence for some but not all of the years that I owned it. Box 3: I designate the
properties as my principal residences for some or all of the years that I owned them." The box is
0 with no property, 3 with more than one property, and for one property 1 when its years designated
(line 3 of Form T2091(IND)) are at least its years owned (line 7) less one, else 2.

It records one `PrincipalResidenceDesignationBox`, not an `ItemsTotalLine`: the box is one figure,
not a total of the properties.
"""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any, ClassVar

from tax_calculator.domain.artifact import Artifact, ArtifactKind
from tax_calculator.domain.capability import CapabilityResult, capability
from tax_calculator.domain.parameters.datasets import ParameterDataset
from tax_calculator.domain.parameters.rounding_only import RoundingOnly
from tax_calculator.domain.record_list import RecordList
from tax_calculator.jurisdictions.ca.capabilities.principal_residence_rows import PrincipalResidenceRows
from tax_calculator.jurisdictions.ca.trace import PrincipalResidenceDesignationBox as DesignationBoxLine


@capability(identifier="principal_residence_designation_box")
class PrincipalResidenceDesignationBoxCapability(PrincipalResidenceRows):
    """Produces `output`: the designation box of Schedule 3 line 17900, as a whole number."""

    PRODUCES: ClassVar[Mapping[str, type]] = {"output": int}

    def __init__(
        self,
        rounding: ParameterDataset[RoundingOnly],
        properties: ArtifactKind[RecordList],
        output: ArtifactKind[int],
    ) -> None:
        """Wire the capability: its rounding dataset, the record list read, the kind produced."""
        super().__init__(rounding, properties, output)
        self._output = output

    def compute(self, inputs: tuple[Artifact[Any], ...]) -> CapabilityResult:
        rows = self._rows(inputs)
        if not rows:
            box = 0
            line = DesignationBoxLine(self._output, 0, 0, 0, box)
        elif len(rows) > 1:
            box = 3
            line = DesignationBoxLine(self._output, len(rows), 0, 0, box)
        else:
            row = rows[0]
            box = 1 if row.designated >= row.owned - 1 else 2
            line = DesignationBoxLine(self._output, 1, row.designated, row.owned, box)
        return CapabilityResult(outputs=(Artifact(self._output, box),), trace=(line,))
