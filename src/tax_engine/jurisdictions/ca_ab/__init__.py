"""Alberta (`CA-AB`): its artifact catalog, the `ca-ab/...` datasets, its capabilities and its
manifest.

Importing the package imports its `capabilities` package.
"""

NAMESPACE = "ca-ab"

from tax_engine.jurisdictions.ca_ab import capabilities  # noqa: E402

__all__ = ["NAMESPACE", "capabilities"]
