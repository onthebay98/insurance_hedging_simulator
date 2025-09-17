# Ensure src/ on path
import sys, pathlib
repo_root = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(repo_root / "src"))

from insurance_hedging_simulator import AnnuityCertain
from insurance_hedging_simulator.curve import ZeroCurve
from insurance_hedging_simulator.curve_risk import dv01_curve
from insurance_hedging_simulator.hedge_swap import size_dv01_hedge_payer_fixed
from insurance_hedging_simulator.stress import (
    shock_parallel_bp, shock_keyrate_bp, run_stresses_on_liability_and_hedge
)

def main():
    pillars = [0.5, 1, 2, 5, 10, 30]
    zeros   = [0.030, 0.031, 0.033, 0.036, 0.038, 0.039]   # mild upward slope
    curve = ZeroCurve(pillars, zeros)

    liab = AnnuityCertain(payment=100.0, n_payments=20)
    pv = liab.pv(curve=curve)
    d01 = dv01_curve(liab, curve, bp=1.0)

    print("=== End-to-End: Liability -> Hedge -> Stress ===")
    print(f"Base PV (liability): {pv:,.2f}")
    print(f"Parallel DV01 (liability): {d01:,.2f} per 1bp")

    swap = size_dv01_hedge_payer_fixed(d01, curve, maturity_years=10, payments_per_year=1)
    print(f"Sized hedge: payer-fixed {swap.maturity_years}y, notional ~ {swap.notional:,.2f}")
    print(f"Fixed rate locked at par: {swap.fixed_rate*100:.3f}%")

    shocks = [
        ("Parallel +100bp", shock_parallel_bp(curve, +100)),
        ("Parallel -100bp", shock_parallel_bp(curve, -100)),
        ("+25bp @ 2y",  shock_keyrate_bp(curve, pillars.index(2.0),  +25)),
        ("+25bp @ 5y",  shock_keyrate_bp(curve, pillars.index(5.0),  +25)),
        ("+25bp @ 30y", shock_keyrate_bp(curve, pillars.index(30.0), +25)),
    ]
    rows = run_stresses_on_liability_and_hedge(liab, curve, swap, shocks)

    print("\nStress P&L (currency units):")
    for r in rows:
        print(f"{r['shock']:<18}  Liability: {r['liability_pnl']:>9.2f}  "
              f"Hedge: {r['hedge_pnl']:>9.2f}  Net: {r['net_pnl']:>9.2f}")

if __name__ == "__main__":
    main()
