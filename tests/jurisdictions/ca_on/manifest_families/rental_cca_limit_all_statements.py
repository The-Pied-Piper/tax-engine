"""The CA-ON manifest's CCA limit over all rental statements: one limit for the person across the
statements of Form T776.

Guide T4036, "Limits on CCA": "If you own more than one rental property, you have to calculate your
overall net income or loss for the year from all your rental properties before you can claim CCA.
If you are a partner, include the net rental income or loss from your T5013 slip in the
calculation. Combine the rental income and loss from all your properties, even if they belong to
different classes. ... You cannot use CCA to create or increase a rental loss." Example, Salvador:
net rental income of 1,500, 2,000 and (4,000), an overall loss of (500), so "he cannot claim any
CCA on his rental buildings or appliances".

These are steps of the return's own form (the once-per-return group, in `03z_t776_cca_limit_all_
statements.yaml`, no `form:` key): the form exports each statement's net income before CCA (in
`03z_t776_cca_pool_statement.yaml`), and the return totals it, floors it at 0, and refuses the CCA
claimed on the person's own properties over all the statements (line 9936 of an owner or co-owner
statement, 0 for a partner statement) when above that limit.
"""

from __future__ import annotations

from tax_calculator.domain.capabilities.at_most import AtMost
from tax_calculator.domain.capabilities.record_total import RecordTotal
from tax_calculator.domain.capabilities.sum_not_below_zero import SumNotBelowZero
from tax_calculator.domain.manifest import CapabilitySelection
from tax_calculator.jurisdictions.ca.catalog import (
    RENTAL_CCA_CLAIMS_TOTAL,
    RENTAL_CCA_LIMIT_ALL_STATEMENTS,
    RENTAL_CCA_TOTAL_CLAIM,
    RENTAL_INCOME_BEFORE_CCA_TOTAL,
)
from tests.jurisdictions.ca_on.manifest_families import t776

INPUTS: frozenset[str] = frozenset()

OUTPUTS = frozenset({"ca/rental_cca_total_claim"})

STEPS = {
    # Guide T4036 "Combine the rental income and loss from all your properties": the total of each
    # statement's net rental income or loss before CCA, over the statements of the form.
    CapabilitySelection(
        name="core/record_total",
        params={},
        consumes={"records": "ca/t776.rental_income_before_cca"},
        produces={"output": "ca/rental_income_before_cca_total"},
    ),
    # Guide T4036 "You cannot use CCA to create or increase a rental loss": the most the CCA of all
    # the statements may be is the overall figure, or 0 when it is negative.
    CapabilitySelection(
        name="core/sum_not_below_zero",
        params={},
        consumes={"parts": ("ca/rental_income_before_cca_total",)},
        produces={"output": "ca/rental_cca_limit_all_statements"},
    ),
    # T776 "Line 9936: Total CCA claim for the year" on the person's own properties (IT-195R4
    # (docs/cra-forms-2025/web/it195r4-rental-property-cca-restrictions.txt, web page) para 2),
    # over the statements of the form: a partner statement's line 9936 is not in it.
    CapabilitySelection(
        name="core/record_total",
        params={},
        consumes={"records": "ca/t776.rental_cca_claim_on_own_properties"},
        produces={"output": "ca/rental_cca_claims_total"},
    ),
    # The claims of every statement together, refused when above the overall limit, not capped.
    CapabilitySelection(
        name="core/at_most",
        params={},
        consumes={
            "amount": "ca/rental_cca_claims_total",
            "bound": "ca/rental_cca_limit_all_statements",
        },
        produces={"output": "ca/rental_cca_total_claim"},
    ),
}

WIRING = {
    (
        RecordTotal,
        frozenset({t776.RENTAL_INCOME_BEFORE_CCA_PER_STATEMENT}),
        frozenset({RENTAL_INCOME_BEFORE_CCA_TOTAL}),
    ),
    (
        SumNotBelowZero,
        frozenset({RENTAL_INCOME_BEFORE_CCA_TOTAL}),
        frozenset({RENTAL_CCA_LIMIT_ALL_STATEMENTS}),
    ),
    (
        RecordTotal,
        frozenset({t776.RENTAL_CCA_CLAIM_ON_OWN_PROPERTIES_PER_STATEMENT}),
        frozenset({RENTAL_CCA_CLAIMS_TOTAL}),
    ),
    (
        AtMost,
        frozenset({RENTAL_CCA_CLAIMS_TOTAL, RENTAL_CCA_LIMIT_ALL_STATEMENTS}),
        frozenset({RENTAL_CCA_TOTAL_CLAIM}),
    ),
}
