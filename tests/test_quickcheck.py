from insurance_hedging_simulator.liabilities import (
    AnnuityCertain, DeferredAnnuityCertain, LifeAnnuityImmediate
)
from insurance_hedging_simulator.risk_helpers import effective_duration, dv01

def test_quickcheck_monotonicity():
    r_low, r_high = 0.02, 0.05
    C, N, D = 100.0, 20, 5
    age = 65

    ac = AnnuityCertain(payment=C, n_payments=N)
    assert ac.pv(r_low) > ac.pv(r_high)

    dac = DeferredAnnuityCertain(payment=C, n_payments=N, defer_years=D)
    assert dac.pv(r_low) < ac.pv(r_low)

    lai = LifeAnnuityImmediate(payment=C, n_payments=N, issue_age=age)
    assert lai.pv(r_low) < ac.pv(r_low)

def test_duration_dv01_signs():
    r = 0.03
    ac = AnnuityCertain(payment=100.0, n_payments=20)
    dur = effective_duration(ac, r)
    d01 = dv01(ac, r)
    assert dur > 0
    assert d01 > 0
