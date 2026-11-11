"""Finding the capabilities of a package by walking its modules, so no list names them.

`capabilities_in` imports every module under a package and returns the classes decorated with
`@capability` that each defines.
"""

from __future__ import annotations

import importlib
import inspect
import pkgutil
from types import ModuleType

from tax_engine.domain.capability import Capability


def capabilities_in(package: ModuleType) -> list[type[Capability]]:
    """The capability classes defined in `package` and its submodules, sorted by identifier.

    A class is taken only from the module that defines it, so one imported elsewhere is not found
    twice. An undecorated subclass of a decorated class has no identifier and is left out.
    """
    modules = [package]
    modules += [
        importlib.import_module(info.name)
        for info in pkgutil.walk_packages(package.__path__, f"{package.__name__}.")
    ]
    found: list[type[Capability]] = []
    for module in modules:
        for _, member in inspect.getmembers(module, inspect.isclass):
            if (
                issubclass(member, Capability)
                and member.identifier() is not None
                and member.__module__ == module.__name__
                and member not in found
            ):
                found.append(member)
    return sorted(found, key=lambda cls: cls.identifier() or "")
