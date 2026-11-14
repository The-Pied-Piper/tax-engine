"""British Columbia (`CA-BC`): its artifact catalog, the `ca-bc/...` datasets, its capabilities and
its manifest.

Importing the package imports its `capabilities` package.
"""

NAMESPACE = "ca-bc"

from tax_engine.jurisdictions.ca_bc import capabilities  # noqa: E402

__all__ = ["NAMESPACE", "capabilities"]
