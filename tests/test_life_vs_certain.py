from insurance_hedging_simulator import AnnuityCertain, LifeAnnuityImmediate
from insurance_hedging_simulator.curve import ZeroCurve

def test_life_annuity_pv_below_certain_annuity_pv():
    pillars = [0.5, 1, 2, 5, 10, 20]
    zeros   = [0.030, 0.031, 0.033, 0.036, 0.038, 0.039]
    curve = ZeroCurve(pillars, zeros)

    C, N, age = 100.0, 20, 65
    ac  = AnnuityCertain(payment=C, n_payments=N)
    lai = LifeAnnuityImmediate(payment=C, n_payments=N, issue_age=age)

    assert lai.pv(curve=curve) < ac.pv(curve=curve)
