import math
from dataclasses import dataclass
from typing import List, Tuple

from .curve import ZeroCurve


def build_schedule(
    maturity_years: int, payments_per_year: int = 1
) -> Tuple[List[float], List[float]]:
    """Annual by default. Returns (pay_times, accruals)."""
    n = maturity_years * payments_per_year
    accrual = 1.0 / payments_per_year
    times = [accrual * (i + 1) for i in range(n)]
    accruals = [accrual] * n
    return times, accruals


def swap_annuity(curve: ZeroCurve, pay_times: List[float], accruals: List[float]) -> float:
    """Sum_i accrual_i * DF(t_i)."""
    return sum(a * curve.df(t) for t, a in zip(pay_times, accruals))


def par_swap_rate(curve: ZeroCurve, maturity_years: int, payments_per_year: int = 1) -> float:
    """K = (1 - DF(T)) / annuity."""
    pay_times, accruals = build_schedule(maturity_years, payments_per_year)
    ann = swap_annuity(curve, pay_times, accruals)
    T = pay_times[-1]
    return (1.0 - curve.df(T)) / ann


def swap_pv_payer_fixed(
    curve: ZeroCurve,
    notional: float,
    maturity_years: int,
    payments_per_year: int,
    fixed_rate: float,
) -> float:
    """
    PV(payer fixed) = PV(float) - PV(fixed).
    PV(float) ~ notional * (1 - DF(T)) for a spot-start par-style swap.
    PV(fixed) = notional * K * annuity(shocked curve).
    """
    pay_times, accruals = build_schedule(maturity_years, payments_per_year)
    T = pay_times[-1]
    ann = swap_annuity(curve, pay_times, accruals)
    pv_float = notional * (1.0 - curve.df(T))
    pv_fixed = notional * fixed_rate * ann
    return pv_float - pv_fixed


@dataclass
class SizedSwap:
    maturity_years: int
    payments_per_year: int
    pay_fixed: bool  # True = payer-fixed, False = receiver-fixed
    notional: float
    fixed_rate: float  # locked at base par

    def pv(self, curve: ZeroCurve) -> float:
        """
        PV for this swap under the given curve. Uses the same payer-fixed
        pricing function and flips the sign if this is receiver-fixed.
        """
        base = swap_pv_payer_fixed(
            curve=curve,
            notional=self.notional,
            maturity_years=self.maturity_years,
            payments_per_year=self.payments_per_year,
            fixed_rate=self.fixed_rate,
        )
        return base if self.pay_fixed else -base


def size_dv01_hedge_payer_fixed(
    liability_dv01: float,
    curve: ZeroCurve,
    maturity_years: int = 10,
    payments_per_year: int = 1,
) -> SizedSwap:
    """
    For MVP: DV01 per unit notional of a par swap ≈ swap annuity (sign depends on side).
    If liability DV01 > 0, we choose payer-fixed (negative DV01) to offset it.
    """
    pay_times, accruals = build_schedule(maturity_years, payments_per_year)
    ann = swap_annuity(curve, pay_times, accruals)
    dv01_per_notional = ann / 10000.0  # <-- convert bp to decimal
    notional = liability_dv01 / dv01_per_notional
    fixed = par_swap_rate(curve, maturity_years, payments_per_year)
    return SizedSwap(
        maturity_years=maturity_years,
        payments_per_year=payments_per_year,
        pay_fixed=True,
        notional=notional,
        fixed_rate=fixed,
    )
