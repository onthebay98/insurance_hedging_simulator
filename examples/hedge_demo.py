# Ensure src on path for direct runs
import sys, pathlib
repo_root = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(repo_root / "src"))

from insurance_hedging_simulator import AnnuityCertain
from insurance_hedging_simulator.curve import ZeroCurve
from insurance_hedging_simulator.curve_risk import (
    dv01_curve, effective_duration_curve, keyrate_durations, keyrate_dv01s
)
from insurance_hedging_simulator.hedge_swap import size_dv01_hedge_payer_fixed
from insurance_hedging_simulator.stress import (
    shock_parallel_bp, shock_keyrate_bp, run_stresses_on_liability_and_hedge
)

def solve_2x2(a11, a12, b1, a21, a22, b2):
    det = a11*a22 - a12*a21
    if abs(det) < 1e-12:
        raise RuntimeError("Singular system while sizing KR01 hedge")
    n1 = ( b1*a22 - b2*a12) / det
    n2 = (-b1*a21 + b2*a11) / det
    return n1, n2

def main():
    # Base curve (continuous zeros)
    pillars = [0.5, 1, 2, 5, 10, 20]
    zeros   = [0.030, 0.031, 0.033, 0.036, 0.038, 0.039]
    curve = ZeroCurve(pillars, zeros)

    # Liability
    liab = AnnuityCertain(payment=100.0, n_payments=20)
    pv   = liab.pv(curve=curve)
    d01  = dv01_curve(liab, curve, bp=1.0)
    dpar = effective_duration_curve(liab, curve, bp=1.0)

    KEY_TENORS = [10.0, 20.0]
    key_idx = [pillars.index(t) for t in KEY_TENORS]
    krd_liab  = keyrate_durations(liab, curve, key_indices=key_idx, bp=1.0)   # dimensionless
    kr01_liab = keyrate_dv01s(liab, curve, key_indices=key_idx, bp=1.0)       # dollars per 1bp

    print("=== Liability ===")
    print(f"PV: {pv:,.2f} | Parallel Duration: {dpar:,.2f} | DV01: {d01:,.2f}")
    for t in KEY_TENORS:
        print(f" KRD {t:>4.0f}y: {krd_liab[t]:.3f}   KR01 {t:>4.0f}y: {kr01_liab[t]:.3f}")

    # Reference payer-fixed swaps normalized so DV01=1.0 (any base notional works; we'll rescale)
    swap10 = size_dv01_hedge_payer_fixed(1.0, curve, maturity_years=10, payments_per_year=1)
    swap20 = size_dv01_hedge_payer_fixed(1.0, curve, maturity_years=20, payments_per_year=1)

    # KR01s for each swap at 10y & 20y
    kr01_s10 = keyrate_dv01s(swap10, curve, key_indices=key_idx, bp=1.0)
    kr01_s20 = keyrate_dv01s(swap20, curve, key_indices=key_idx, bp=1.0)

    # Convert to per-unit-notional sensitivities
    s10_perN = {t: kr01_s10[t] / swap10.notional for t in KEY_TENORS}
    s20_perN = {t: kr01_s20[t] / swap20.notional for t in KEY_TENORS}

    # Solve n10, n20 so hedge KR01s match -liability KR01s at 10y/20y
    n10, n20 = solve_2x2(
        s10_perN[10.0], s20_perN[10.0], -kr01_liab[10.0],
        s10_perN[20.0], s20_perN[20.0], -kr01_liab[20.0],
    )
    swap10.notional = n10
    swap20.notional = n20

    # Report DV01s
    d01_s10 = dv01_curve(swap10, curve, bp=1.0)
    d01_s20 = dv01_curve(swap20, curve, bp=1.0)
    print("\n=== Hedge (two swaps: payer-fixed 10y & 20y) ===")
    print(f"10y swap notional ~ {swap10.notional:,.2f}, par fixed ~ {swap10.fixed_rate*100:.3f}%")
    print(f"20y swap notional ~ {swap20.notional:,.2f}, par fixed ~ {swap20.fixed_rate*100:.3f}%")
    print(f"DV01s — Liability: {d01:,.2f}, 10y: {d01_s10:,.2f}, 20y: {d01_s20:,.2f}, Net: {d01 + d01_s10 + d01_s20:,.2f}")

    # Net KR01s after hedge (should be ~0 at 10y & 20y)
    for t in KEY_TENORS:
        net = (
            kr01_liab[t]
            + keyrate_dv01s(swap10, curve, [pillars.index(t)], 1.0)[t]
            + keyrate_dv01s(swap20, curve, [pillars.index(t)], 1.0)[t]
        )
        print(f"Net KR01 {int(t)}y: {net:+.4f}")

    # Shocks
    shocks = [
        ("Parallel +100bp", shock_parallel_bp(curve, +100)),
        ("Parallel -100bp", shock_parallel_bp(curve, -100)),
        ("+25bp @ 2y",  shock_keyrate_bp(curve, pillars.index(2.0),  +25)),
        ("+25bp @ 5y",  shock_keyrate_bp(curve, pillars.index(5.0),  +25)),
        ("+25bp @ 10y", shock_keyrate_bp(curve, pillars.index(10.0), +25)),
        ("+25bp @ 20y", shock_keyrate_bp(curve, pillars.index(20.0), +25)),
    ]

    rows = run_stresses_on_liability_and_hedge(liab, curve, [swap10, swap20], shocks)

    # Pretty header
    shock_w = 18
    num_w   = 14

    print("\n=== Stress P&L (currency units) ===")
    print(f"{'Shock':<{shock_w}}{'Liability':>{num_w}}{'Hedge':>{num_w}}{'Net':>{num_w}}")
    print("-" * (shock_w + 3*num_w))

    for r in rows:
        print(
            f"{r['shock']:<{shock_w}}"
            f"{r['liability_pnl']:>{num_w}.2f}"
            f"{r['hedge_pnl']:>{num_w}.2f}"
            f"{r['net_pnl']:>{num_w}.2f}"
        )


if __name__ == "__main__":
    main()
