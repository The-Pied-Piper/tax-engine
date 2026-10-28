"""A made-up module that registers on import, in a registry of its own."""

from tax_calculator.domain.registry import Namespace, Registry


class Thing:
    """A made-up thing to register."""


Registry[type[object]]().register(Namespace.of(Thing).identifier("thing"), Thing)
