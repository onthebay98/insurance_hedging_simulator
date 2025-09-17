# src/insurance_hedging_simulator/liabilities.py
from dataclasses import dataclass, field
from typing import List, Tuple, Literal, Optional, overload
import math
from .curve import ZeroCurve

Compounding = Literal["continuous", "annual"]


def discount_factor(t: float, r: float, compounding: Compounding = "continuous") -> float:
    """Flat-rate discount factor."""
    if t <= 0:
        return 1.0
    if compounding == "continuous":
        return math.exp(-r * t)
    elif compounding == "annual":
        return (1.0 + r) ** (-t)
    raise ValueError("Unsupported compounding")


@dataclass
class AnnuityCertain:
    payment: float
    n_payments: int
    compounding: Compounding = "continuous"

    def cashflows(self) -> List[Tuple[float, float]]:
        # (time in years, amount), end-of-period payments at t = 1..N
        return [(t, self.payment) for t in range(1, self.n_payments + 1)]

    # Overloads tell the type checker exactly how this is used.
    @overload
    def pv(self, r: float, curve: None = ...) -> float: ...
    @overload
    def pv(self, r: None = ..., curve: ZeroCurve = ...) -> float: ...

    def pv(self, r: Optional[float] = None, curve: Optional[ZeroCurve] = None) -> float:
        # Runtime guards that line up with the overloads
        if curve is not None and r is not None:
            raise ValueError("Provide exactly one of r or curve, not both")
        if curve is not None:
            return sum(cf * curve.df(t) for t, cf in self.cashflows())
        if r is not None:
            return sum(cf * discount_factor(t, r, self.compounding) for t, cf in self.cashflows())
        raise ValueError("Provide exactly one of r or curve")


@dataclass
class DeferredAnnuityCertain:
    payment: float
    n_payments: int
    defer_years: int
    compounding: Compounding = "continuous"

    def cashflows(self) -> List[Tuple[float, float]]:
        start = self.defer_years + 1
        end = self.defer_years + self.n_payments
        return [(t, self.payment) for t in range(start, end + 1)]

    @overload
    def pv(self, r: float, curve: None = ...) -> float: ...
    @overload
    def pv(self, r: None = ..., curve: ZeroCurve = ...) -> float: ...

    def pv(self, r: Optional[float] = None, curve: Optional[ZeroCurve] = None) -> float:
        if curve is not None and r is not None:
            raise ValueError("Provide exactly one of r or curve, not both")
        if curve is not None:
            return sum(cf * curve.df(t) for t, cf in self.cashflows())
        if r is not None:
            return sum(cf * discount_factor(t, r, self.compounding) for t, cf in self.cashflows())
        raise ValueError("Provide exactly one of r or curve")


@dataclass
class GompertzMakeham:
    A: float = 0.0005  # age-independent hazard
    B: float = 0.00003
    c: float = 1.08

    def survival(self, x: float, t: float) -> float:
        """{}_{t}p_x = exp( -A t - (B/ln c) * (c^{x+t} - c^{x}) )."""
        if t <= 0:
            return 1.0
        if self.c <= 0 or self.c == 1.0:
            raise ValueError("c must be > 0 and != 1")
        return math.exp(-self.A * t - (self.B / math.log(self.c)) * (self.c ** (x + t) - self.c ** x))


@dataclass
class LifeAnnuityImmediate:
    payment: float
    n_payments: int
    issue_age: float
    mortality: GompertzMakeham = field(default_factory=GompertzMakeham)
    compounding: Compounding = "continuous"

    def cashflows(self) -> List[Tuple[float, float]]:
        # unweighted cash flows; survival applied in PV
        return [(t, self.payment) for t in range(1, self.n_payments + 1)]

    @overload
    def pv(self, r: float, curve: None = ...) -> float: ...
    @overload
    def pv(self, r: None = ..., curve: ZeroCurve = ...) -> float: ...

    def pv(self, r: Optional[float] = None, curve: Optional[ZeroCurve] = None) -> float:
        if curve is not None and r is not None:
            raise ValueError("Provide exactly one of r or curve, not both")

        pv_val = 0.0
        if curve is not None:
            for t, cf in self.cashflows():
                surv = self.mortality.survival(self.issue_age, t)
                pv_val += cf * surv * curve.df(t)
            return pv_val

        if r is not None:
            for t, cf in self.cashflows():
                surv = self.mortality.survival(self.issue_age, t)
                pv_val += cf * surv * discount_factor(t, r, self.compounding)
            return pv_val

        raise ValueError("Provide exactly one of r or curve")
