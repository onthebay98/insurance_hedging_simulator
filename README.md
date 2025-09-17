# Insurance Hedging Simulator

A quantitative sandbox for modeling insurance liabilities, valuing them on yield curves, and managing their **interest rate risk**.
It mirrors core tasks in **insurance asset-liability management (ALM)** and **fixed-income risk analytics**:

* Model liabilities like annuities.
* Value them under zero-coupon curves.
* Compute risk sensitivities — parallel duration, DV01, key-rate exposures.
* Build swap hedges to **neutralize specific curve nodes**.
* Stress test the combined liability + hedge portfolio.

---

## ✨ Current Capabilities

### Liability Modeling

* **Annuity Certain (Immediate)** — fixed annual payments for N years
* **Deferred Annuity Certain** — same, but payments start after a deferral period
* **Life Annuity (Immediate)** — contingent on survival (Gompertz–Makeham mortality)

### Curves & Valuation

* **Flat-rate valuation** (continuous/annual compounding)
* **Zero-curve valuation** (`ZeroCurve` with interpolation between pillars)

### Risk Analytics

* **Effective Duration** — years of sensitivity to a parallel shift
* **DV01** — \$ change per 1bp parallel shift in the curve
* **Key-Rate Durations (KRDs)** — sensitivity to local bumps at specific tenors
* **Key-Rate DV01s (KR01s)** — dollar exposure per 1bp at specific nodes

### Hedging

* **Plain-vanilla swaps** (payer-fixed at par)
* **DV01-matching hedge**: size a single swap to offset parallel risk
* **Node-targeted hedging**: size multiple swaps (e.g., 10y & 20y) to neutralize curve-shape risk
* Output hedge notionals, fixed rates, and net exposures

### Stress Testing

* **Parallel shifts** (±100bp)
* **Key-rate bumps** (e.g., +25bp at 2y, 5y, 10y, 20y)
* **P\&L attribution**: liability, hedge, and net effect

---

## 📊 Example Outputs

### A) Flat-Rate Demo (`examples/liability_demo.py`)

```text
AnnuityCertain PV @2% : 1,631.97
AnnuityCertain PV @5% : 1,232.90
DeferredAnnuity PV @2%: 1,476.67
LifeAnnuity PV @2%    : 1,504.60

AnnuityCertain Duration (eff) @2% : 9.84 years
AnnuityCertain DV01 @2%           : 1.61 per 1bp
```

* PV falls as rates rise (2% → 5%).
* Deferred annuity < life annuity (deferral cuts out guaranteed early payments).
* Life annuity < certain (mortality reduces PV and duration).
* DV01 ≈ PV × Duration × 1e-4 consistency check holds.

---

### B) Curve-Based Exposures (`examples/risk_exposures_demo.py`)

```text
AnnuityCertain (curve-based)
PV (base): 1,376.30
Parallel Duration: 9.20  |  DV01: 1.27 per 1bp
Key-Rate Durations (per 1bp):
   2y : 0.351
   5y : 1.320
  10y : 3.973
  20y : 3.482
```

* Curve shows where cashflow risk lives:
  – Early payments → short-tenor exposure.
  – Later payments → 10y/20y exposures dominate.

---

### C) Node-Targeted Hedging (`examples/end_to_end_demo.py`)

```text
=== End-to-End: Liability → Node-Targeted Hedge → Stress ===
Base PV (liability): 1,376.30
Parallel Duration (liability): 9.20 years  |  DV01: 1.27 per 1bp
Node 10y — KRD: 3.973  |  KR01: 0.547
Node 20y — KRD: 3.482  |  KR01: 0.479

=== Hedge Portfolio (payer-fixed at par) ===
10y swap — notional: 600.26  |  fixed: 3.842%
20y swap — notional: 433.58  |  fixed: 3.935%
Parallel DV01 — Liability: 1.27, 10y: -0.51, 20y: -0.61  →  Net: +0.14 per 1bp
Net KR01s (per 1bp): 10y=-0.0000  20y=+0.0000

=== Stress P&L (currency units) ===
Shock                  Liability         Hedge           Net
------------------------------------------------------------
Parallel +100bp          -118.93        104.89        -14.03
Parallel -100bp           135.03       -120.39         14.64
+25bp @ 2y                 -1.21          0.48         -0.72
+25bp @ 5y                 -4.52          1.81         -2.71
+25bp @ 10y               -13.54         13.51         -0.03
+25bp @ 20y               -11.79         11.71         -0.09
```

**Interpretation**

* Hedge works exactly where targeted (10y & 20y nodes → Net ≈ 0).
* Parallel risk largely hedged, though some residual remains.
* Short-end (2y/5y) exposures still open → could add more instruments.
* This mirrors **real-world ALM**: you can’t hedge everything with one trade; you choose instruments to match exposures at key tenors.

---

## 🧪 Quickstart

```bash
# Python 3.12+ recommended
python -m venv .venv
source .venv/bin/activate
pip install -e .
pytest  # run tests

# run examples
python examples/liability_demo.py
python examples/risk_exposures_demo.py
python examples/hedge_demo.py
python examples/end_to_end_demo.py
```

---

## 🗂️ Project Structure

```
.github/workflows/
  ci.yml                         # GitHub Actions CI (tests on push/PR)
examples/
  liability_demo.py              # Flat-rate PV, duration, DV01
  risk_exposures_demo.py         # Curve-based DV01 & KRDs
  hedge_demo.py                  # Single DV01-matching swap
  end_to_end_demo.py             # Node-targeted hedging (10y & 20y)
src/insurance_hedging_simulator/
  liabilities.py                 # annuity models (certain, deferred, life)
  curve.py                       # ZeroCurve with interpolation
  curve_risk.py                  # DV01, duration, KRDs, KR01s
  hedge_swap.py                  # swap annuity, par rate, PV, sizing
  stress.py                      # curve shocks & P&L attribution
tests/
  test_hedge_sizing.py           # hedge sizing validation
  test_curve_parity.py           # curve math checks
pyproject.toml / requirements.txt
README.md
```

---

## 🎯 Why This Matters

This project demonstrates a **miniature ALM workflow**:

1. **Model** the liability cashflows.
2. **Value** them under a realistic zero curve.
3. **Quantify** interest rate risk by tenor (DV01, KRD, KR01).
4. **Construct** hedge portfolios (swaps) to neutralize exposures.
5. **Validate** under stress scenarios.