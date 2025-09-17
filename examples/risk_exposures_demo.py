import sys, pathlib
repo_root = pathlib.Path(__file__).resolve().parents[1]
src_path = repo_root / "src"
if str(src_path) not in sys.path:
    sys.path.insert(0, str(src_path))

from insurance_hedging_simulator import (
    AnnuityCertain, DeferredAnnuityCertain, LifeAnnuityImmediate
)
from insurance_hedging_simulator.curve import ZeroCurve
from insurance_hedging_simulator.curve_risk import (
    dv01_curve, effective_duration_curve, keyrate_durations
)

def main():
    # Example curve (continuous zeros), shaped like a mild upward slope
    pillars = [0.5, 1, 2, 5, 10, 20]
    zeros   = [0.030, 0.031, 0.033, 0.036, 0.038, 0.039]
    curve = ZeroCurve(pillars, zeros)

    C, N, D, age = 100.0, 20, 5, 65
    ac  = AnnuityCertain(payment=C, n_payments=N)
    dac = DeferredAnnuityCertain(payment=C, n_payments=N, defer_years=D)
    lai = LifeAnnuityImmediate(payment=C, n_payments=N, issue_age=age)

    for name, obj in [("AnnuityCertain", ac), ("DeferredAnnuity", dac), ("LifeAnnuity", lai)]:
        pv   = obj.pv(curve=curve)
        dpar = effective_duration_curve(obj, curve, bp=1.0)
        d01  = dv01_curve(obj, curve, bp=1.0)
        krds = keyrate_durations(obj, curve, key_indices=[0,1,2,3,4,5], bp=1.0)  # e.g., 0.5y, 2y, 5y, 20y

        print(f"\n{name} (curve-based)")
        print(f"PV (base): {pv:,.2f}")
        print(f"Parallel Duration: {dpar:,.2f}  |  DV01: {d01:,.2f} per 1bp")
        print("Key-Rate Durations (per 1bp):")
        for tenor in sorted(krds):
            print(f"  {tenor:>4.1f}y : {krds[tenor]:.3f}")

if __name__ == '__main__':
    main()
