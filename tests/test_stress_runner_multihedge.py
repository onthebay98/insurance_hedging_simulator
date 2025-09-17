from insurance_hedging_simulator import AnnuityCertain
from insurance_hedging_simulator.curve import ZeroCurve
from math import isclose

def test_curve_equals_flat_when_zeros_flat():
    C, N, r = 100.0, 20, 0.03
    ac = AnnuityCertain(payment=C, n_payments=N)
    pv_flat = ac.pv(r=r)

    pillars = [0.5,1,2,5,10,30]
    zeros = [r]*len(pillars)
    curve = ZeroCurve(pillars, zeros)
    pv_curve = ac.pv(curve=curve)

    assert isclose(pv_flat, pv_curve, rel_tol=1e-6)
