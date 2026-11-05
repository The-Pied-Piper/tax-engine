"""Finding the parameter parsers of a package by walking its modules, so no list names them.

A parser package is any package whose modules define parser classes (decorated with
`@parameter_parser`, declaring their `kind`). `parsers_in` imports every module under it and
returns the parser classes each one defines, so adding a parser is adding its module.
"""

from __future__ import annotations

import importlib
import inspect
import pkgutil
from types import ModuleType

from tax_engine.domain.parameters.kind import ParameterKind


def parsers_in(package: ModuleType) -> list[type]:
    """The parser classes defined in `package` and its submodules, sorted by class name.

    A parser class is a class that declares a `ParameterKind` as its own `kind` attribute. Only a
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
            if (
                isinstance(inspect.getattr_static(member, "kind", None), ParameterKind)
                and member.__module__ == module.__name__
                and member not in found
            ):
                found.append(member)
    return sorted(found, key=lambda cls: cls.__name__)
