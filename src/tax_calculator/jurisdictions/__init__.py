"""Jurisdiction packages: one package per jurisdiction, holding everything specific to it.

Each package has an `__init__.py` declaring its `NAMESPACE`, a `catalog.py` declaring its
artifact kinds as `CATALOG`, `manifests/` selecting capabilities and `parameters/` holding its
datasets. Importing a package registers only its capabilities; `JURISDICTIONS.register()`
registers catalogs.
Real jurisdiction names appear only here and in the mirrored `tests/jurisdictions/`.
"""
