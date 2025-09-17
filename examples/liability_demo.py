# examples/liability_demo.py
import sys, pathlib
repo_root = pathlib.Path(__file__).resolve().parents[1]
src_path = repo_root / "src"
if str(src_path) not in sys.path:
    sys.path.insert(0, str(src_path))

from insurance_hedging_simulator import (
    AnnuityCertain,
    DeferredAnnuityCertain,
    LifeAnnuityImmediate,
    effective_duration,
    dv01,
)

def fmt(x): return f"{x:,.2f}"

def main():
    r_low, r_high = 0.02, 0.05
    C, N, D = 100.0, 20, 5
    age = 65

    ac  = AnnuityCertain(payment=C, n_payments=N)
    dac = DeferredAnnuityCertain(payment=C, n_payments=N, defer_years=D)
    lai = LifeAnnuityImmediate(payment=C, n_payments=N, issue_age=age)

    pv_ac_low  = ac.pv(r_low)
    pv_ac_high = ac.pv(r_high)
    pv_dac     = dac.pv(r_low)
    pv_lai     = lai.pv(r_low)

    dur_ac  = effective_duration(ac, r_low)
    d01_ac  = dv01(ac, r_low)
    # dur_lai = effective_duration(lai, r_low)
    # d01_lai = dv01(lai, r_low)

    print("\n== Liability demo (annual payments, continuous comp) ==")
    print(f"AnnuityCertain PV @2% : {fmt(pv_ac_low)}")
    print(f"AnnuityCertain PV @5% : {fmt(pv_ac_high)}")
    print(f"DeferredAnnuity PV @2%: {fmt(pv_dac)} (deferral lowers PV)")
    print(f"LifeAnnuity PV @2%    : {fmt(pv_lai)} (mortality lowers PV)")
    print()
    print(f"AnnuityCertain Duration (eff) @2% : {dur_ac:,.2f} years")
    print(f"AnnuityCertain DV01 @2%           : {d01_ac:,.2f} per 1bp")
    # print(f"LifeAnnuity Duration (eff) @2%    : {dur_lai:,.2f} years")
    # print(f"LifeAnnuity DV01 @2%              : {d01_lai:,.2f} per 1bp")

if __name__ == "__main__":
    main()
