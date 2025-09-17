import sys, pathlib
repo_root = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(repo_root / "src"))

from insurance_hedging_simulator.scenarios import make_curve, generate_vasicek_scenarios
from insurance_hedging_simulator.liabilities import AnnuityCertain

pillars = [0.5, 1, 2, 5, 10, 20]
curve_up = make_curve("upward", pillars, base=0.03, slope=0.01)

ac = AnnuityCertain(payment=100.0, n_payments=20)
print("PV on upward curve:", round(ac.pv(curve=curve_up), 2))

scens = generate_vasicek_scenarios(
    r0=0.03, kappa=0.5, theta=0.03, sigma=0.01,
    dt=1/12, n_steps=12, n_paths=200, pillars=pillars, seed=42
)
print("Paths shape:", scens["short_rate_paths"].shape)
print("Example curve zeros T=30y on path 0, step 12:",
      scens["curves"][0][12].zero_rates[-1])
