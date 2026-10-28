from tax_calculator import build_tax_computation
from tax_calculator.domain.jurisdiction_code import JurisdictionCode


def test_bundled_jurisdiction_data_composes() -> None:
    engine = build_tax_computation()
    forms = engine.compose(JurisdictionCode("CA-ON"), 2025)

    assert len(forms.forms) == 48
    order = forms.form("ca-on/return").composition.order
    assert order
    assert len(order) == len({(type(step), step.consumes, step.produces) for step in order})
