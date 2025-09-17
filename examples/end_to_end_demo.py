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
    print("=== End-to-End: Liability → Node-Targeted Hedge → Stress ===")

    # 1) Curve with 20y long end (matches 20y liability horizon)
    pillars = [0.5, 1, 2, 5, 10, 20]
    zeros   = [0.030, 0.031, 0.033, 0.036, 0.038, 0.039]  # mild upward slope
    curve = ZeroCurve(pillars, zeros)

    # 2) Liability: 20 annual payments of 100
    liab = AnnuityCertain(payment=100.0, n_payments=20)
    pv    = liab.pv(curve=curve)
    d01   = dv01_curve(liab, curve, bp=1.0)
    dpar  = effective_duration_curve(liab, curve, bp=1.0)

    # Focus nodes: where exposure is largest for this product
    KEY_TENORS = [10.0, 20.0]
    key_idx    = [pillars.index(t) for t in KEY_TENORS]
    krd_liab   = keyrate_durations(liab, curve, key_indices=key_idx, bp=1.0)   # dimensionless
    kr01_liab  = keyrate_dv01s(liab, curve, key_indices=key_idx, bp=1.0)       # $ per 1bp

    print(f"Base PV (liability): {pv:,.2f}")
    print(f"Parallel Duration (liability): {dpar:,.2f} years  |  DV01: {d01:,.2f} per 1bp")
    for t in KEY_TENORS:
        print(f"Node {int(t)}y — KRD: {krd_liab[t]:.3f}  |  KR01: {kr01_liab[t]:.3f}")

    # 3) Build two payer-fixed swaps (10y & 20y) and size by KR01 matching
    # Reference swaps normalized via DV01=1.0 so we can get KR01-per-notional cleanly
    swap10 = size_dv01_hedge_payer_fixed(1.0, curve, maturity_years=10, payments_per_year=1)
    swap20 = size_dv01_hedge_payer_fixed(1.0, curve, maturity_years=20, payments_per_year=1)

    kr01_s10 = keyrate_dv01s(swap10, curve, key_indices=key_idx, bp=1.0)
    kr01_s20 = keyrate_dv01s(swap20, curve, key_indices=key_idx, bp=1.0)

    # Sensitivities per unit notional
    s10_perN = {t: kr01_s10[t] / swap10.notional for t in KEY_TENORS}
    s20_perN = {t: kr01_s20[t] / swap20.notional for t in KEY_TENORS}

    # Solve for actual notionals n10, n20 to neutralize KR01s at 10y & 20y
    n10, n20 = solve_2x2(
        s10_perN[10.0], s20_perN[10.0], -kr01_liab[10.0],
        s10_perN[20.0], s20_perN[20.0], -kr01_liab[20.0],
    )
    swap10.notional = n10
    swap20.notional = n20

    # Parallel DV01 check (not a target here, but useful context)
    d01_s10 = dv01_curve(swap10, curve, bp=1.0)
    d01_s20 = dv01_curve(swap20, curve, bp=1.0)
    d01_net = d01 + d01_s10 + d01_s20

    print("\n=== Hedge Portfolio (payer-fixed at par) ===")
    print(f"10y swap — notional: {swap10.notional:,.2f}  |  fixed: {swap10.fixed_rate*100:.3f}%")
    print(f"20y swap — notional: {swap20.notional:,.2f}  |  fixed: {swap20.fixed_rate*100:.3f}%")
    print(f"Parallel DV01 — Liability: {d01:,.2f}, 10y: {d01_s10:,.2f}, 20y: {d01_s20:,.2f}  →  Net: {d01_net:+.2f} per 1bp")

    # Net KR01s after hedging (should be ~0 at 10y & 20y)
    net_kr01 = {}
    for t in KEY_TENORS:
        idx = pillars.index(t)
        net_kr01[t] = (
            kr01_liab[t]
            + keyrate_dv01s(swap10, curve, [idx], 1.0)[t]
            + keyrate_dv01s(swap20, curve, [idx], 1.0)[t]
        )
    print("Net KR01s (per 1bp): " + "  ".join([f"{int(t)}y={net_kr01[t]:+,.4f}" for t in KEY_TENORS]))

    # 4) Stress: parallel and node bumps (show hedge actually works where we targeted)
    shocks = [
        ("Parallel +100bp", shock_parallel_bp(curve, +100)),
        ("Parallel -100bp", shock_parallel_bp(curve, -100)),
        ("+25bp @ 2y",  shock_keyrate_bp(curve, pillars.index(2.0),  +25)),
        ("+25bp @ 5y",  shock_keyrate_bp(curve, pillars.index(5.0),  +25)),
        ("+25bp @ 10y", shock_keyrate_bp(curve, pillars.index(10.0), +25)),
        ("+25bp @ 20y", shock_keyrate_bp(curve, pillars.index(20.0), +25)),
    ]
    rows = run_stresses_on_liability_and_hedge(liab, curve, [swap10, swap20], shocks)

    # Pretty table
    shock_w, num_w = 18, 14
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

    # 5) Narrative cues (for anyone reading the console)
    print("\nNotes:")
    print("- We matched KR01s at 10y & 20y, so shape risk at those nodes is ~neutral (see tiny Net under +25bp @10y/@20y).")
    print("- Parallel DV01 wasn’t targeted, so a small residual remains (see ~±Net under ±100bp).")
    print("- Short-end nodes (2y/5y) still show residuals; add a 5y instrument or a 3×3 solve to tighten further if desired.")

if __name__ == "__main__":
    main()
