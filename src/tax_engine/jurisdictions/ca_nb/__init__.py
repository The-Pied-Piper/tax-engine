"""New Brunswick (`CA-NB`): its artifact catalog, the `ca-nb/...` datasets, its capabilities, its
trace lines and its manifest.

Importing the package imports its `capabilities`, `trace` and `trace_english` packages.
"""

NAMESPACE = "ca-nb"

from tax_engine.jurisdictions.ca_nb import capabilities, trace, trace_english  # noqa: E402

__all__ = ["NAMESPACE", "capabilities", "trace", "trace_english"]
