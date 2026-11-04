"""Finding the capabilities of a package by walking its modules, so no list names them.

A capabilities package is any package whose modules define classes decorated with `@capability`.
`capabilities_in` imports every module under it and returns the decorated classes each one
defines, so adding a capability is adding its module.
"""

from __future__ import annotations

import importlib
import inspect
import pkgutil
from types import ModuleType

from tax_engine.domain.capability import Capability


def capabilities_in(package: ModuleType) -> list[type[Capability]]:
    """The capability classes defined in `package` and its submodules, by identifier.

    Only a class defined in a module is taken from it, so one imported from elsewhere is not
    found twice. A subclass of a decorated class that is not itself decorated carries no
    identifier and is left out.
    """
    found: list[type[Capability]] = []
    for info in pkgutil.walk_packages(package.__path__, f"{package.__name__}."):
        module = importlib.import_module(info.name)
        for _, member in inspect.getmembers(module, inspect.isclass):
            if (
                issubclass(member, Capability)
                and member.__module__ == module.__name__
                and member.identifier() is not None
            ):
                found.append(member)
    return sorted(found, key=lambda cls: cls.identifier() or "")
