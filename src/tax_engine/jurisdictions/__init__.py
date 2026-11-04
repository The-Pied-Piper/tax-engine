"""Jurisdiction packages: one package per jurisdiction, holding everything specific to it.

Each package has an `__init__.py` declaring its `NAMESPACE`, a `catalog.py` declaring its
artifact kinds as `CATALOG`, `manifests/` selecting capabilities and `parameters/` holding its
datasets. Importing a package registers nothing: `JURISDICTIONS.register()` registers catalogs and
`JURISDICTIONS.register_capabilities()` the capabilities.
Real jurisdiction names appear only here and in the mirrored `tests/jurisdictions/`.
"""
