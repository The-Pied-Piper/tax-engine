"""Ontario (`CA-ON`): its artifact catalog and the `ca-on/...` datasets.

Importing the package imports its `capabilities` package, which holds Ontario's capabilities
(none today).
"""

NAMESPACE = "ca-on"

from tax_engine.jurisdictions.ca_on import capabilities  # noqa: E402

__all__ = ["NAMESPACE", "capabilities"]
