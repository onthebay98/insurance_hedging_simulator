from insurance_hedging_simulator import AnnuityCertain
from insurance_hedging_simulator.curve import ZeroCurve
from insurance_hedging_simulator.hedge_swap import size_dv01_hedge_payer_fixed
from insurance_hedging_simulator.stress import (
    run_stresses_on_liability_and_hedge,
    shock_parallel_bp,
)


def test_stress_runner_handles_multiple_swaps_and_netting():
    pillars = [0.5, 1, 2, 5, 10, 20]
    zeros = [0.030, 0.031, 0.033, 0.036, 0.038, 0.039]
    curve = ZeroCurve(pillars, zeros)

    liab = AnnuityCertain(payment=100.0, n_payments=20)

    # Two arbitrary reference swaps (not necessarily perfect hedges)
    s10 = size_dv01_hedge_payer_fixed(0.5, curve, maturity_years=10, payments_per_year=1)
    s20 = size_dv01_hedge_payer_fixed(0.8, curve, maturity_years=20, payments_per_year=1)

    shocks = [("Parallel +100bp", shock_parallel_bp(curve, +100))]
    rows = run_stresses_on_liability_and_hedge(liab, curve, [s10, s20], shocks)

    assert len(rows) == 1
    r = rows[0]
    # net = liability_pnl + hedge_pnl
    assert abs(r["net_pnl"] - (r["liability_pnl"] + r["hedge_pnl"])) < 1e-9
