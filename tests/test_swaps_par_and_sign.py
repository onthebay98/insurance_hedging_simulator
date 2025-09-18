from insurance_hedging_simulator.curve import ZeroCurve
from insurance_hedging_simulator.curve_risk import dv01_curve
from insurance_hedging_simulator.hedge_swap import (
    SizedSwap,
    par_swap_rate,
    swap_pv_payer_fixed,
)


def test_par_swap_has_zero_pv_and_payer_fixed_has_negative_dv01():
    pillars = [0.5, 1, 2, 5, 10, 20]
    zeros = [0.030, 0.031, 0.033, 0.036, 0.038, 0.039]
    curve = ZeroCurve(pillars, zeros)

    maty = 10
    k = par_swap_rate(curve, maturity_years=maty, payments_per_year=1)

    # PV at par should be ~0
    pv = swap_pv_payer_fixed(
        curve, notional=1.0, maturity_years=maty, payments_per_year=1, fixed_rate=k
    )
    assert abs(pv) < 1e-8

    # SizedSwap with pay_fixed=True should have negative DV01 (value rises when rates rise)
    s = SizedSwap(
        maturity_years=maty, payments_per_year=1, pay_fixed=True, notional=1.0, fixed_rate=k
    )
    d01 = dv01_curve(s, curve, bp=1.0)
    assert d01 < 0.0
