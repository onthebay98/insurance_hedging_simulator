from math import isclose
from insurance_hedging_simulator import AnnuityCertain
from insurance_hedging_simulator.curve import ZeroCurve
from insurance_hedging_simulator.curve_risk import dv01_curve
from insurance_hedging_simulator.hedge_swap import size_dv01_hedge_payer_fixed, swap_annuity, build_schedule

def test_parallel_dv01_is_near_zero_after_hedge():
    pillars = [0.5, 1, 2, 5, 10, 30]
    zeros   = [0.030, 0.031, 0.033, 0.036, 0.038, 0.039]
    curve = ZeroCurve(pillars, zeros)

    liab = AnnuityCertain(payment=100.0, n_payments=20)
    d01_liab = dv01_curve(liab, curve, bp=1.0)

    swap = size_dv01_hedge_payer_fixed(d01_liab, curve, maturity_years=10, payments_per_year=1)

    # DV01 of swap per notional ~= annuity/10,000
    times, accruals = build_schedule(swap.maturity_years, swap.payments_per_year)
    ann = swap_annuity(curve, times, accruals) / 10000.0
    d01_swap_total = - ann * swap.notional   # payer-fixed sign

    net = d01_liab + d01_swap_total
    assert isclose(net, 0.0, rel_tol=0, abs_tol=0.5), f"Residual DV01 too large: {net}"
