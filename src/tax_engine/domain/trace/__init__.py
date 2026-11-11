"""The structured trace: what each capability did, recorded as facts, never text.

Jurisdiction-specific lines live in `tax_engine.jurisdictions.<package>.trace`; rendering is in the
adapters.
"""

from __future__ import annotations

# Each feature module's `__all__` is re-exported, so a class added to an existing module needs no
# edit here; a new feature module adds its name to each of the three lists below.
from tax_engine.domain.trace import (
    arithmetic,
    base,
    blank,
    choices,
    forms,
    rate_tables,
    record_lists,
)
from tax_engine.domain.trace.arithmetic import *  # noqa: F403
from tax_engine.domain.trace.base import *  # noqa: F403
from tax_engine.domain.trace.blank import *  # noqa: F403
from tax_engine.domain.trace.choices import *  # noqa: F403
from tax_engine.domain.trace.forms import *  # noqa: F403
from tax_engine.domain.trace.rate_tables import *  # noqa: F403
from tax_engine.domain.trace.record_lists import *  # noqa: F403

__all__ = (
    arithmetic.__all__
    + base.__all__
    + blank.__all__
    + choices.__all__
    + forms.__all__
    + rate_tables.__all__
    + record_lists.__all__
)
