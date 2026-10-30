"""CA-ON 2025 end to end: return au."""

from __future__ import annotations

from typing import Any

from tax_engine.domain.worksheet import Worksheet
from tax_engine.jurisdictions.ca.capabilities.disposition_proceeds import DispositionProceeds
from tax_engine.jurisdictions.ca.catalog import (
    BOND_PROCEEDS,
    CAPITAL_GAIN,
    CRYPTO_ASSET_PROCEEDS,
    OTHER_FORECLOSURE_PROCEEDS,
    QFFP_FORECLOSURE_PROCEEDS,
    QFFP_PROCEEDS,
    QSBCS_PROCEEDS,
    REAL_ESTATE_PROCEEDS,
    REFUND_OR_BALANCE_OWING,
    SHARE_PROCEEDS,
    TAXABLE_CAPITAL_GAINS,
    TOTAL_PAYABLE,
)
from tests.jurisdictions.ca_on.end_to_end.support import (
    D,
    Disposition,
    RealEstateDisposition,
    compute,
)

PROCEEDS_LINES = (
    QSBCS_PROCEEDS,
    QFFP_PROCEEDS,
    QFFP_FORECLOSURE_PROCEEDS,
    SHARE_PROCEEDS,
    REAL_ESTATE_PROCEEDS,
    BOND_PROCEEDS,
    CRYPTO_ASSET_PROCEEDS,
    OTHER_FORECLOSURE_PROCEEDS,
)


def raised(rows: tuple[Disposition, ...], extra: str) -> tuple[Disposition, ...]:
    """`rows` with `extra` added to the proceeds and to the adjusted cost base of each."""
    return tuple((str(D(p) + D(extra)), str(D(c) + D(extra)), o) for p, c, o in rows)


def raised_real_estate(
    rows: tuple[RealEstateDisposition, ...], extra: str
) -> tuple[RealEstateDisposition, ...]:
    """`rows` with `extra` added to the proceeds and to the adjusted cost base of each."""
    return tuple((str(D(p) + D(extra)), str(D(c) + D(extra)), o, flag) for p, c, o, flag in rows)


def return_au(extra: str = "0") -> Worksheet:
    """Return AU's inputs, as in `returns/2025_return_au.yaml`: employment income of 60000 and
    the share, real estate, crypto-asset and other foreclosure rows, each a chosen figure.
    `extra` is added to the proceeds and to the adjusted cost base of every row, which leaves
    every gain or loss as it is.
    """
    shares: tuple[Disposition, ...] = (("12000", "8000", "100"), ("3000", "4000", "50"))
    real_estate: tuple[RealEstateDisposition, ...] = (("90000", "60000", "2000", 0),)
    crypto: tuple[Disposition, ...] = (("5000", "7000", "0"),)
    foreclosures: tuple[Disposition, ...] = (("1000", "1500", "0"),)
    given: dict[str, Any] = {
        "real_estate_dispositions": raised_real_estate(real_estate, extra),
        "crypto_asset_dispositions": raised(crypto, extra),
        "other_foreclosure_dispositions": raised(foreclosures, extra),
        "income_tax_deducted": "14000",
    }
    return compute("60000", raised(shares, extra), "0", "0", "0", "0", "0", **given)


def test_return_au_totals_column_2_of_each_list_on_its_proceeds_line() -> None:
    # Line 4 (13199): 12000 + 3000 = 15000, the second row a loss (3000 - 4000 - 50) whose proceeds
    # still count. Line 5 (13599): 90000. Line 7 (15200): 5000, a loss row (5000 - 7000). Line 8
    # (15499): 1000, a loss row (1000 - 1500). Lines 1, 2, 3 and 6 (10699, 10999, 12399, 15199)
    # have no rows: 0.
    worksheet = return_au()

    assert worksheet.get(QSBCS_PROCEEDS).value == D("0")
    assert worksheet.get(QFFP_PROCEEDS).value == D("0")
    assert worksheet.get(QFFP_FORECLOSURE_PROCEEDS).value == D("0")
    assert worksheet.get(SHARE_PROCEEDS).value == D("15000")
    assert worksheet.get(REAL_ESTATE_PROCEEDS).value == D("90000")
    assert worksheet.get(BOND_PROCEEDS).value == D("0")
    assert worksheet.get(CRYPTO_ASSET_PROCEEDS).value == D("5000")
    assert worksheet.get(OTHER_FORECLOSURE_PROCEEDS).value == D("1000")
    for kind in PROCEEDS_LINES:
        assert isinstance(worksheet.producer_of(kind), DispositionProceeds), kind.identifier


def test_the_proceeds_totals_feed_nothing_so_the_return_does_not_change_with_them() -> None:
    # Adding 1000 to the proceeds and to the adjusted cost base of every row leaves every gain or
    # loss (column 5) as it is: capital gains of 28350, taxable capital gains of 14175.00, total
    # payable of 13029.69 and a refund (line 48400) of 970.31 with the chosen 14000 deducted. Only
    # the proceeds totals move.
    base = return_au()
    more = return_au("1000")

    assert more.get(SHARE_PROCEEDS).value == D("17000")
    assert more.get(REAL_ESTATE_PROCEEDS).value == D("91000")
    assert more.get(CRYPTO_ASSET_PROCEEDS).value == D("6000")
    assert more.get(OTHER_FORECLOSURE_PROCEEDS).value == D("2000")
    for worksheet in (base, more):
        assert worksheet.get(CAPITAL_GAIN).value == D("28350")
        assert worksheet.get(TAXABLE_CAPITAL_GAINS).value == D("14175.00")
        assert worksheet.get(TOTAL_PAYABLE).value == D("13029.69")
        assert worksheet.get(REFUND_OR_BALANCE_OWING).value == D("-970.31")
