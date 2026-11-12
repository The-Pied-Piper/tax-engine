# Jurisdiction packages

Everything specific to one jurisdiction lives in one package under `tax_engine.jurisdictions`.
Real jurisdiction names appear only there and in the mirrored `tests/jurisdictions/`.

## Layout

| Part | Holds |
| --- | --- |
| `__init__.py` | `NAMESPACE = "..."`, the namespace of every identifier the package declares. Declare it at the top, before importing any module that uses `@capability`, which resolves it on import. A subpackage that declares identifiers repeats the namespace to inherit it. |
| `catalog.py` or `catalog/` | The artifact kinds, on a `CATALOG`. |
| `units.py` | Optional. The units it declares, on a `UNITS` `UnitCatalog` in the package's namespace, each with `declare(local_id, singular, plural, placement, spaced)`: where the text goes (before or after the number) and whether a space separates it from the figure. A manifest names one by its full identifier, `unit: <namespace>/<local_id>`; a province package does not inherit its country's units, so a manifest names them with the country's namespace. |
| `manifests/` | Manifests, see [Manifest format](manifest-format.md). |
| `forms/` | Parts of forms that other manifests import. |
| `parameters/` | Parameter datasets, see [Parameter files](parameter-files.md). |
| `capabilities/` | Capability classes decorated with `@capability`. |
| `parameter_parsers/` | Parsers of the package's own parameter kinds. |
| `parameter_shapes/` | The value objects those parameter kinds produce. |
| `trace/`, `trace_english/` | Trace lines of the package's own and the renderers of their English text. |

The `core` package is the same shape with an empty catalog and no data folders: its `capabilities`
and `parameter_parsers` hold the generic mechanisms.

## Registration

Nothing registers by being imported, apart from the decorators that fill the shared registry of
English trace renderers. `tax_engine.registrations` lists the packages in `JURISDICTIONS` and builds
the registries once each for the composition root: `artifact_kinds()` from every `catalog`,
`units()` from every `units` module, `capabilities()` from every `capabilities` package and
`parameter_parsers()` from every `parameter_parsers` package, found by walking their modules. A new capability or parser is a new
module in its package; a new jurisdiction is importing its package and listing it in
`JURISDICTIONS`. `CORE_PACKAGES` names the one package outside `jurisdictions` whose decorators fill
a shared registry: the English trace renderers.

A new module of trace lines needs a renderer module of the same name in `trace_english`, imported
by that package.

## Layering

A jurisdiction package never imports the application layer, the wiring, or `adapters.outbound`. The
one exception is its `parameter_parsers`, which may import `adapters.outbound.parameter_parser` and
`adapters.outbound.yaml_support`, to extend the parser base class and read their dataset through
`YamlNode`. `lint-imports` enforces this.
