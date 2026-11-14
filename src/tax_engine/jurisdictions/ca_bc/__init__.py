"""British Columbia (`CA-BC`): its artifact catalog, the `ca-bc/...` datasets, its capabilities,
its trace lines and its manifest.

Importing the package imports its `capabilities`, `trace` and `trace_english` packages.
"""

NAMESPACE = "ca-bc"

from tax_engine.jurisdictions.ca_bc import capabilities, trace, trace_english  # noqa: E402

__all__ = ["NAMESPACE", "capabilities", "trace", "trace_english"]
