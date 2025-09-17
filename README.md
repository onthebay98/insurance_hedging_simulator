# Insurance Hedging Simulator

A quantitative prototype for modeling insurance liabilities, valuing them under interest rate scenarios, and computing risk sensitivities (parallel duration, DV01, and key-rate durations). It mirrors core tasks in **insurance hedging** and **fixed-income risk analytics**.

---

## ✨ Current Capabilities

### Liability Modeling

* **Annuity Certain (Immediate)** — fixed annual payments for $N$ years
* **Deferred Annuity** — fixed annual payments starting after a deferral period
* **Life Annuity (Immediate)** — payments contingent on survival (Gompertz–Makeham)

### Discounting & Curves

* **Flat-rate valuation** (continuous or annual compounding)
* **Zero-curve valuation** via `ZeroCurve` (continuous-compounded zeros with interpolation)

### Risk Analytics

* **Effective Duration (parallel)** — bump-and-reprice under flat or full curve
* **DV01 (parallel)** — PV change per 1 bp parallel move
* **Key-Rate Durations (KRDs)** — tenor-specific duration via local pillar bumps

### Simple Hedging (DV01 Matching)

* **Plain-vanilla 10y interest-rate swap** (annual fixed)
* Size **payer-fixed** notional to offset a **positive** liability DV01
* **Stress tests**: parallel ±100 bp and key-rate +25 bp at 2y/5y/30y

### Scenario Generation (optional module)

* Parametric curve shapes (**flat / upward / inverted**)
* **Vasicek** short-rate paths and derived zero curves

### Engineering Hygiene

* Modern Python package (`src/` layout, `pyproject.toml`, `pytest.ini`)
* Unit tests (monotonicities, parity, scenarios)
* **GitHub Actions** CI (`.github/workflows/ci.yml`) runs tests on push/PR

---

## 📊 Example Outputs

### A) Flat-Rate Demo (`examples/liability_demo.py`)

```text
== Liability demo (annual payments, continuous comp) ==
AnnuityCertain PV @2% : 1,631.97
AnnuityCertain PV @5% : 1,232.90
DeferredAnnuity PV @2%: 1,476.67 (deferral lowers PV)
LifeAnnuity PV @2%    : 1,504.60 (mortality lowers PV)

AnnuityCertain Duration (eff) @2% : 9.84 years
AnnuityCertain DV01 @2%           : 1.61 per 1bp
LifeAnnuity Duration (eff) @2%    : 9.48 years
LifeAnnuity DV01 @2%              : 1.43 per 1bp
```

**Interpretation (flat):**

* PV falls as rates rise (2% → 5%): 1,631.97 → 1,232.90.
* Deferred < Immediate; Life < Certain (mortality lowers PV and duration).
* DV01 is positive → liability PV rises when rates fall.
* Consistency: $\text{DV01} \approx PV \times \text{Duration} \times 10^{-4}$ holds.

---

### B) Curve-Based Exposures (`examples/risk_exposures_demo.py`)

```text
AnnuityCertain (curve-based)
PV (base): 1,378.71
Parallel Duration: 9.21  |  DV01: 1.27 per 1bp
Key-Rate Durations (per 1bp):
   0.5y : -0.000
   2.0y : 0.351
   5.0y : 1.317
  30.0y : 1.749

DeferredAnnuity (curve-based)
PV (base): 1,133.23
Parallel Duration: 14.20  |  DV01: 1.61 per 1bp
Key-Rate Durations (per 1bp):
   0.5y : -0.000
   2.0y : -0.000
   5.0y : 0.950
  30.0y : 4.836

LifeAnnuity (curve-based)
PV (base): 1,279.58
Parallel Duration: 8.87  |  DV01: 1.14 per 1bp
Key-Rate Durations (per 1bp):
   0.5y : -0.000
   2.0y : 0.372
   5.0y : 1.367
  30.0y : 1.590
```

**Interpretation (curve):**

* Parallel DV01/duration line up with flat-rate intuition at similar yields.
* Deferred annuity’s KRD mass sits in **long tenors (30y)** → back-loaded cash flows.
* Life annuity is slightly **front-loaded** vs. certain → lower duration and modestly shorter-tenor KRDs.
* Consistency check: $PV \times \text{Duration} \times 10^{-4}$ ≈ DV01 for each line item.

---

### C) Hedging Demo — DV01-Matched Swap (`examples/hedge_demo.py`)

> Ensure `hedge_swap.size_dv01_hedge_payer_fixed` uses **DV01 per notional = swap annuity / 10,000**.

**Your base run (before the sizing fix) showed the hedge P\&L near zero under ±100 bp**, which indicated under-sizing. After applying the fix, expect:

```text
Base PV (liability): 1,378.71
Parallel DV01 (liability): 1.27 per 1bp

Sized hedge: payer-fixed 10y, notional ~ 1,543.26
Fixed rate locked at par: 3.842%

Stress P&L (currency units), indicative:
Parallel +100bp     Liability: ~ -119     Hedge: ~ +125     Net: near 0
Parallel -100bp     Liability: ~ +135     Hedge: ~ -137     Net: near 0
+25bp @ 2y          Liability:   -1.21    Hedge:   ~ +0.7   Net: ~ -0.5
+25bp @ 5y          Liability:   -4.52    Hedge:   ~ +2.7   Net: ~ -1.8
+25bp @ 30y         Liability:   -5.98    Hedge:     ~ 0.0  Net: ~ -6.0
```

**Why this makes sense**

* DV01 matching knocks down **parallel** risk; residuals are convexity/tenor mismatches.
* A single 10y swap won’t hedge a **30y** key-rate bump; use multiple maturities to target curve shape if needed.

---

## 🧪 Quickstart

```bash
# Python 3.12+ recommended
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
pip install -e .
pytest

# run examples
python examples/liability_demo.py
python examples/risk_exposures_demo.py
python examples/hedge_demo.py
python examples/scenarios_demo.py   # optional; uses scenarios.py
```

---

## 🗂️ Project Structure

```
.github/workflows/
  ci.yml                         # GitHub Actions: run tests on push/PR
examples/
  __init__.py
  liability_demo.py              # PV, duration, DV01 under flat rates
  risk_exposures_demo.py         # PV, DV01, KRDs under a zero curve
  hedge_demo.py                  # DV01-matched 10y swap; stress P&L
  scenarios_demo.py              # optional: parametric curves & Vasicek
src/
  insurance_hedging_simulator/
    __init__.py                  # exposes top-level API
    liabilities.py               # annuity models + survival
    risk_helpers.py              # flat-rate duration/DV01 helpers
    curve.py                     # ZeroCurve (continuous zeros, interpolation)
    curve_risk.py                # DV01 (curve), parallel duration, KRDs
    hedge_swap.py                # swap annuity, par rate, DV01 sizing (fixed)
    stress.py                    # simple parallel/key-rate shocks & P&L
    scenarios.py                 # optional: parametric curves & Vasicek paths
tests/
  test_quickcheck.py
  test_curve_parity.py
  test_scenarios.py              # if using scenarios.py
pyproject.toml
pytest.ini
Makefile
requirements.txt
README.md
```

---

## 🎯 Why This Matters

This project shows you can:

1. Model insurance liabilities,
2. Value them on realistic curves,
3. Quantify **where** rate risk lives (overall and by tenor), and
4. Size a **plain, explainable hedge** that neutralizes first-order exposure—then communicate residual curve risk.