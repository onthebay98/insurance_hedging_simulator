# Ensure src on path for direct runs
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
    # Base curve (continuous zeros)
    pillars = [0.5, 1, 2, 5, 10, 30]
    zeros   = [0.030, 0.031, 0.033, 0.036, 0.038, 0.039]
    curve = ZeroCurve(pillars, zeros)

    # Liability
    liab = AnnuityCertain(payment=100.0, n_payments=20)
    pv   = liab.pv(curve=curve)
    d01  = dv01_curve(liab, curve, bp=1.0)

    print("Base PV (liability):", f"{pv:,.2f}")
    print("Parallel DV01 (liability):", f"{d01:,.2f} per 1bp")

    # Size payer-fixed swap to offset positive DV01
    swap = size_dv01_hedge_payer_fixed(d01, curve, maturity_years=10, payments_per_year=1)
    print(f"\nSized hedge: payer-fixed {swap.maturity_years}y, notional ~ {swap.notional:,.2f}")
    print(f"Fixed rate locked at par: {swap.fixed_rate*100:.3f}%")

    # Build simple shocks
    shocks = []
    shocks.append(("Parallel +100bp", shock_parallel_bp(curve, +100)))
    shocks.append(("Parallel -100bp", shock_parallel_bp(curve, -100)))
    # Key-rate bumps at indices matching 2y, 5y, 30y
    idx2 = pillars.index(2.0)
    idx5 = pillars.index(5.0)
    idx30 = pillars.index(30.0)
    shocks.append(("+25bp @ 2y",  shock_keyrate_bp(curve, idx2, +25)))
    shocks.append(("+25bp @ 5y",  shock_keyrate_bp(curve, idx5, +25)))
    shocks.append(("+25bp @ 30y", shock_keyrate_bp(curve, idx30, +25)))

    rows = run_stresses_on_liability_and_hedge(liab, curve, swap, shocks)

    print("\nStress P&L (currency units):")
    for r in rows:
        print(f"{r['shock']:<18}  Liability: {r['liability_pnl']:>9.2f}  "
              f"Hedge: {r['hedge_pnl']:>9.2f}  Net: {r['net_pnl']:>9.2f}")

if __name__ == "__main__":
    main()
