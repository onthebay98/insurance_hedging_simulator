# Insurance Hedging Simulator (MVP)

Quant-first mini-project to model insurance liabilities, discount under flat rates, and compute duration/DV01.

## What it does (Day 1)
- Annuity certain, deferred annuity, simplified life annuity (Gompertz–Makeham survival).
- Flat-rate PV with continuous/annual compounding.
- Effective duration and DV01 via bump-and-reprice.
- Sanity checks & unit tests.

## Quickstart
```bash
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
pytest