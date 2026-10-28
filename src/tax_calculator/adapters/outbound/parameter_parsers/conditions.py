"""Parses `conditions` datasets: a count and a list of conditions into a ConditionList."""

from __future__ import annotations

from decimal import Decimal

from tax_calculator.adapters.outbound.parameter_parsers.registry import parameter_parser
from tax_calculator.adapters.outbound.yaml_support import YamlNode
from tax_calculator.domain.errors import DomainError, InvalidConditionsError
from tax_calculator.domain.parameters.conditions import (
    CONDITIONS,
    Condition,
    ConditionList,
    ConditionPart,
    ConditionTest,
)

_CONDITION_KEYS = frozenset({"text", "parts"})
_PART_KEYS = frozenset({"tests"})
_TEST_KEYS = frozenset({"reads", "position", "relation"})
_OPTIONAL_TEST_KEYS = frozenset({"than", "against"})


@parameter_parser
class ConditionsParser:
    """Parser for `conditions` datasets: `count_when_any_applies` (a quoted whole number) and
    `conditions`, each a `text` and `parts`; each part holds `tests`, each a `reads`, a quoted
    `position`, a `relation` and one of a quoted decimal `than` and a quoted position `against`."""

    kind = CONDITIONS
    body_keys = frozenset({"count_when_any_applies", "conditions"})

    def parse(self, document: YamlNode) -> ConditionList:
        """Build a ConditionList from the dataset's count and its conditions, as written."""
        count = document.field("count_when_any_applies").parse_whole_number()
        conditions = tuple(self._condition(entry) for entry in document.field("conditions").items())
        return ConditionList(count_when_any_applies=count, conditions=conditions)

    @staticmethod
    def _condition(entry: YamlNode) -> Condition:
        fields = entry.require_mapping(_CONDITION_KEYS)
        text = fields.field("text").require_string()
        parts = tuple(ConditionsParser._part(part) for part in fields.field("parts").items())
        try:
            return Condition(text=text, parts=parts)
        except DomainError as exc:
            # Name the condition: the value objects do not know where in the list they sit.
            raise InvalidConditionsError(f"{entry.where}: {exc}") from exc

    @staticmethod
    def _part(entry: YamlNode) -> ConditionPart:
        fields = entry.require_mapping(_PART_KEYS)
        tests = tuple(ConditionsParser._test(test) for test in fields.field("tests").items())
        try:
            return ConditionPart(tests=tests)
        except DomainError as exc:
            # Name the part: the value objects do not know where in the list they sit.
            raise InvalidConditionsError(f"{entry.where}: {exc}") from exc

    @staticmethod
    def _test(entry: YamlNode) -> ConditionTest:
        fields = entry.require_mapping(_TEST_KEYS, optional=_OPTIONAL_TEST_KEYS)
        reads = fields.field("reads").require_string()
        position = fields.field("position").parse_whole_number()
        relation = fields.field("relation").require_string()
        than_node = fields.optional_field("than")
        than: Decimal | None = None if than_node is None else than_node.parse_decimal()
        against_node = fields.optional_field("against")
        against = None if against_node is None else against_node.parse_whole_number()
        try:
            return ConditionTest(
                reads=reads, position=position, relation=relation, than=than, against=against
            )
        except DomainError as exc:
            # Name the test: the value objects do not know where in the list they sit.
            raise InvalidConditionsError(f"{entry.where}: {exc}") from exc
