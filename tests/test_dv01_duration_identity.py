import math
from insurance_hedging_simulator import AnnuityCertain
from insurance_hedging_simulator.curve import ZeroCurve
from insurance_hedging_simulator.curve_risk import dv01_curve, effective_duration_curve

def test_dv01_vs_pv_times_duration():
    # Simple upward curve
    pillars = [0.5, 1, 2, 5, 10, 20]
    zeros   = [0.030, 0.031, 0.033, 0.036, 0.038, 0.039]
    curve = ZeroCurve(pillars, zeros)

    liab = AnnuityCertain(payment=100.0, n_payments=20)
    pv   = liab.pv(curve=curve)
    dpar = effective_duration_curve(liab, curve, bp=1.0)
    d01  = dv01_curve(liab, curve, bp=1.0)

    # DV01 ≈ PV * Duration * 1e-4 (continuous comp & small-bump approximation)
    lhs = d01
    rhs = pv * dpar * 1e-4
    assert math.isfinite(lhs) and math.isfinite(rhs)
    # Allow loose tolerance (nonlinearities, discrete payments, curve shape)
    assert abs(lhs - rhs) / max(1.0, abs(rhs)) < 0.02  # within ~2%
