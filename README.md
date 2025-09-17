# Insurance Hedging Simulator

A quantitative prototype for modeling insurance liabilities, valuing them under interest rate scenarios, and computing risk sensitivities (parallel duration, DV01, and key-rate durations). Built to mirror core tasks in **insurance hedging** and **fixed-income risk analytics**.

---

## ✨ Current Capabilities

### Liability Modeling

* **Annuity Certain (Immediate)** — fixed annual payments for $N$ years
* **Deferred Annuity** — fixed annual payments starting after a deferral period
* **Life Annuity (Immediate)** — payments contingent on survival (Gompertz–Makeham)

### Discounting & Curves

* **Flat-rate valuation** (continuous or annual compounding)
* **Zero-curve valuation** via `ZeroCurve` (continuous-compounded zero rates with interpolation)

### Risk Analytics

* **Effective Duration (parallel)** — bump-and-reprice under flat rate or full curve
* **DV01 (parallel)** — PV change per 1 bp parallel move
* **Key-Rate Durations (KRDs)** — tenor-specific duration via local pillar bumps

### Demo & Testing

* Example scripts in `examples/` to reproduce results
* Unit tests for monotonicities and parity checks
* Modern Python project hygiene (`src/` layout, `pyproject.toml`, pytest, black, isort)

---

## 📊 Example Outputs

### A) Flat-Rate Demo

(from `examples/liability_demo.py`, annual payments, continuous comp)

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

* **PV falls as rates rise** (2% → 5%): 1,631.97 → 1,232.90
* **Deferral lowers PV** (1,476.67 < 1,631.97)
* **Mortality lowers PV and shortens duration** (life annuity duration 9.48y < certain 9.84y)
* **DV01 positive** → liability PV rises when rates fall
* Consistency check: $\text{DV01} \approx PV \times \text{Duration} \times 10^{-4}$

  * Annuity-certain: $1{,}631.97 \times 9.84 \times 10^{-4} \approx 1.61$ ✅
  * Life annuity: $1{,}504.60 \times 9.48 \times 10^{-4} \approx 1.43$ ✅

---

### B) Curve-Based Demo

(from `examples/risk_exposures_demo.py` using a mildly upward-sloping zero curve)

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

* **Parallel DV01 and duration** align with flat-rate intuition at similar yield levels.
* **Deferral increases exposure at long tenors**: KRD mass is concentrated at **30y** for the deferred annuity (4.836), reflecting back-loaded cash flows.
* **Mortality front-loads expected payments** slightly: life annuity duration (8.87y) is below certain (9.21y); KRDs tilt modestly toward shorter tenors vs. certain.
* Consistency check again:

  * Annuity-certain: $1{,}378.71 \times 9.21 \times 10^{-4} \approx 1.27$ ✅
  * Deferred: $1{,}133.23 \times 14.20 \times 10^{-4} \approx 1.61$ ✅
  * Life: $1{,}279.58 \times 8.87 \times 10^{-4} \approx 1.13 \approx 1.14$ ✅

> KRDs show **where** along the curve the risk lives. Their sum will be close to (not exactly) the parallel duration because local bumps differ from a true parallel shift and interpolation spreads effects.

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
```

---

## 🗂️ Project Structure

```
src/
  insurance_hedging_simulator/
    __init__.py                 # exposes top-level API (AnnuityCertain, etc.)
    liabilities.py              # annuity models + survival
    risk_helpers.py             # flat-rate duration/DV01 helpers
    curve.py                    # ZeroCurve (continuous zeros, interpolation)
    curve_risk.py               # DV01 (curve), parallel duration, KRDs
examples/
  liability_demo.py             # PV, duration, DV01 under flat rates
  risk_exposures_demo.py        # PV, DV01, KRDs under a zero curve
tests/
  test_quickcheck.py            # monotonicities & sign checks
  test_curve_parity.py          # parity: flat rate vs flat zero curve
pyproject.toml
README.md
```

---

## 🎯 Why This Matters

Insurers carry long-dated, rate-sensitive liabilities. Quantifying **PV**, **parallel DV01**, and **KRDs** is foundational for:

* sizing **hedges** (e.g., selecting swap maturities to neutralize exposures),
* interpreting **scenario P\&L** and **stress** outcomes, and
* explaining **hedge effectiveness** and residual risks to stakeholders.

This prototype shows both **quant modeling** (liability cash flows, mortality, curve risk) and **engineering rigor** (tests, clean packaging) aligned with an insurance hedging / fixed-income analytics role.

---

## 🔭 Planned Extensions

* **Stochastic short-rate model (Vasicek)** to generate rate paths and scenario curves
* **Hedge sizing** with plain-vanilla swaps (DV01 matching) and effectiveness checks
* **Scenario VaR & stress** (pre/post hedge), with concise reporting plots