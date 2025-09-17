from insurance_hedging_simulator import AnnuityCertain
from insurance_hedging_simulator.curve import ZeroCurve
from insurance_hedging_simulator.curve_risk import dv01_curve, keyrate_dv01s
from insurance_hedging_simulator.hedge_swap import size_dv01_hedge_payer_fixed

def solve_2x2(a11, a12, b1, a21, a22, b2):
    det = a11*a22 - a12*a21
    if abs(det) < 1e-12:
        raise RuntimeError("Singular system")
    n1 = ( b1*a22 - b2*a12) / det
    n2 = (-b1*a21 + b2*a11) / det
    return n1, n2

def test_two_node_hedge_neutralizes_10y_20y_kr01s():
    pillars = [0.5, 1, 2, 5, 10, 20]
    zeros   = [0.030, 0.031, 0.033, 0.036, 0.038, 0.039]
    curve = ZeroCurve(pillars, zeros)

    liab = AnnuityCertain(payment=100.0, n_payments=20)
    # Liability KR01s at nodes
    idx10, idx20 = pillars.index(10.0), pillars.index(20.0)
    liab_kr01 = keyrate_dv01s(liab, curve, [idx10, idx20], bp=1.0)

    # Reference swaps with DV01=1.0 (normalization)
    s10 = size_dv01_hedge_payer_fixed(1.0, curve, maturity_years=10, payments_per_year=1)
    s20 = size_dv01_hedge_payer_fixed(1.0, curve, maturity_years=20, payments_per_year=1)

    s10_kr01 = keyrate_dv01s(s10, curve, [idx10, idx20], bp=1.0)
    s20_kr01 = keyrate_dv01s(s20, curve, [idx10, idx20], bp=1.0)

    # per-unit-notional sensitivities
    a11 = s10_kr01[10.0] / s10.notional
    a21 = s10_kr01[20.0] / s10.notional
    a12 = s20_kr01[10.0] / s20.notional
    a22 = s20_kr01[20.0] / s20.notional
    b1  = -liab_kr01[10.0]
    b2  = -liab_kr01[20.0]
    n10, n20 = solve_2x2(a11, a12, b1, a21, a22, b2)

    # Apply notionals
    s10.notional = n10
    s20.notional = n20

    # Check KR01s ~ 0 at 10y & 20y
    net10 = liab_kr01[10.0] + keyrate_dv01s(s10, curve, [idx10])[10.0] + keyrate_dv01s(s20, curve, [idx10])[10.0]
    net20 = liab_kr01[20.0] + keyrate_dv01s(s10, curve, [idx20])[20.0] + keyrate_dv01s(s20, curve, [idx20])[20.0]
    assert abs(net10) < 1e-3    # a fraction of a cent per bp
    assert abs(net20) < 1e-3

    # Parallel DV01 should be small (we didn't target it, so not exactly zero)
    d01_net = dv01_curve(liab, curve) + dv01_curve(s10, curve) + dv01_curve(s20, curve)
    assert abs(d01_net) < 0.3   # ~0.3 currency units per bp max, adjust if needed
