# Insurance Hedging Simulator

A quantitative prototype for modeling insurance liabilities, valuing them under interest rate scenarios, and computing risk sensitivities such as **duration** and **DV01**.

This project demonstrates how an insurer’s long-dated cash flow obligations respond to changes in interest rates, laying the groundwork for hedging and risk management analysis.

---

## ✨ Current Features

### Liability Modeling

* **Annuity Certain (Immediate)** – fixed payments each year for $N$ years.
* **Deferred Annuity** – fixed payments beginning after a deferral period.
* **Life Annuity (Immediate)** – fixed payments contingent on survival, modeled using a **Gompertz–Makeham mortality law**.

### Discounting

* **Flat yield curves** with continuous or annual compounding.
* Present value (PV) of future liability cash flows.

### Risk Analytics

* **Effective Duration** – bump-and-reprice sensitivity of PV to parallel rate shifts.
* **DV01** – dollar value change of liability for a 1 basis point move in rates.
* Basic sanity checks:

  * PV decreases as discount rate increases.
  * Deferred annuity PV < immediate annuity PV.
  * Life annuity PV < certain annuity PV (mortality reduces expected cash flows).

### Demo & Testing

* Example script (`examples/liability_demo.py`) that prints PV, duration, and DV01 for sample liabilities.
* Unit tests to validate monotonicity and sign of sensitivities.
* Modern project layout (`src/` structure, `pyproject.toml`, pytest, black, isort).

---

## 📊 Example Output

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

**Interpretation**

* **PV falls as rates rise:** 2% → 5% drops the annuity-certain PV from **1,631.97** to **1,232.90**.
* **Deferral lowers PV:** deferred annuity PV at 2% = **1,476.67**, which is below the immediate annuity’s **1,631.97**.
* **Mortality lowers PV and shortens duration:** life annuity PV at 2% = **1,504.60** (< **1,631.97**), and its effective duration (**9.48y**) is slightly lower than the certain annuity’s (**9.84y**).
* **DV01 is positive (as expected for liabilities):**

  * Annuity-certain DV01 @2% = **1.61** per 1 bp.
  * Life annuity DV01 @2% = **1.43** per 1 bp.
    Positive DV01 means **PV rises when rates fall**.

### Quick consistency check

For small shifts, $\text{DV01} \approx PV \times \text{Duration} \times 10^{-4}$.

* Annuity-certain: $1{,}631.97 \times 9.84 \times 10^{-4} \approx 1.61$ ✅
* Life annuity: $1{,}504.60 \times 9.48 \times 10^{-4} \approx 1.43$ ✅

---

## 🛠️ Tech Stack

* **Python 3.12+**
* **Dataclasses** for clear financial contract representations.
* **Pytest** for testing liability behavior.
* **Black & isort** for consistent style.
* **Editable install (`pip install -e .`)** with a `src/` project layout.

---

## 🚀 Next Steps (Planned Extensions)

* Support for **full yield curves** (zero curve interpolation, discount factors beyond flat rates).
* **Curve risk analytics**: parallel & key-rate durations.
* **Stochastic rate models** (e.g., Vasicek) to generate scenario paths.
* **Hedge sizing** with swaps or futures to neutralize DV01.
* **Risk reporting**: pre/post hedge metrics, scenario P\&L distributions, stress tests.

---

## 📂 Project Structure

```
insurance_hedging_simulator/
├── src/
│   └── insurance_hedging_simulator/
│       ├── __init__.py
│       ├── liabilities.py
│       ├── risk_helpers.py
├── tests/
│   └── test_quickcheck.py
├── examples/
│   └── liability_demo.py
├── pyproject.toml
├── README.md
```

---