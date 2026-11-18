"""Newfoundland and Labrador (`CA-NL`): its artifact catalog, its capabilities, its trace lines and
its manifest.

Importing the package imports its `capabilities`, `trace` and `trace_english` packages.
"""

NAMESPACE = "ca-nl"

from tax_engine.jurisdictions.ca_nl import capabilities, trace, trace_english  # noqa: E402

__all__ = ["NAMESPACE", "capabilities", "trace", "trace_english"]
