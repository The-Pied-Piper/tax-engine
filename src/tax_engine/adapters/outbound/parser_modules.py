"""Finding the parameter parsers of a package by walking its modules, so no list names them.

`parsers_in` imports every module under a package and returns the `@parameter_parser` classes each
defines.
"""

from __future__ import annotations

import importlib
import inspect
import pkgutil
from types import ModuleType

from tax_engine.adapters.outbound.parameter_parser import is_parser


def parsers_in(package: ModuleType) -> list[type]:
    """The parser classes defined in `package` and its submodules, sorted by class name.

    A parser class is one decorated with `@parameter_parser` itself, not a subclass of one. Only a
    class defined in a module is taken from it, so one imported from elsewhere is not found twice.
    """
    modules = [package]
    modules += [
        importlib.import_module(info.name)
        for info in pkgutil.walk_packages(package.__path__, f"{package.__name__}.")
    ]
    found: list[type] = []
    for module in modules:
        for _, member in inspect.getmembers(module, inspect.isclass):
            if is_parser(member) and member.__module__ == module.__name__ and member not in found:
                found.append(member)
    return sorted(found, key=lambda cls: cls.__name__)
