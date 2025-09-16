from dataclasses import dataclass, field
from typing import List, Tuple, Literal
import math

Compounding = Literal["continuous", "annual"]

def discount_factor(t: float, r: float, compounding: Compounding = "continuous") -> float:
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
        return [(t, self.payment) for t in range(1, self.n_payments + 1)]

    def pv(self, r: float) -> float:
        return sum(cf * discount_factor(t, r, self.compounding) for t, cf in self.cashflows())

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

    def pv(self, r: float) -> float:
        return sum(cf * discount_factor(t, r, self.compounding) for t, cf in self.cashflows())

@dataclass
class GompertzMakeham:
    A: float = 0.0005
    B: float = 0.00003
    c: float = 1.08

    def survival(self, x: float, t: float) -> float:
        if self.c <= 0 or self.c == 1.0:
            raise ValueError("c must be > 0 and != 1")
        return math.exp(
            - self.A * t
            - (self.B / math.log(self.c)) * (self.c ** (x + t) - self.c ** x)
        )

@dataclass
class LifeAnnuityImmediate:
    payment: float
    n_payments: int
    issue_age: float
    mortality: GompertzMakeham = field(default_factory=GompertzMakeham)  # <- fix
    compounding: Compounding = "continuous"

    def cashflows(self) -> List[Tuple[float, float]]:
        return [(t, self.payment) for t in range(1, self.n_payments + 1)]

    def pv(self, r: float) -> float:
        pv_val = 0.0
        for t, cf in self.cashflows():
            surv = self.mortality.survival(self.issue_age, t)
            pv_val += cf * surv * discount_factor(t, r, self.compounding)
        return pv_val
