from dataclasses import dataclass
from typing import List
import bisect, math

@dataclass
class ZeroCurve:
    """Zero (spot) curve with continuous-compounded zero rates at pillar maturities (years)."""
    pillars: List[float]      # e.g., [0.5, 1, 2, 5, 10, 30]
    zero_rates: List[float]   # continuous-compounded, same length as pillars

    def _zero_at(self, t: float) -> float:
        """Linear interpolate zero rate z(t) on pillars. (cont-comp zeros => DF=exp(-z t))"""
        if t <= 0:
            return 0.0
        i = bisect.bisect_left(self.pillars, t)
        if i == 0:
            return self.zero_rates[0]
        if i >= len(self.pillars):
            return self.zero_rates[-1]
        t0, t1 = self.pillars[i-1], self.pillars[i]
        z0, z1 = self.zero_rates[i-1], self.zero_rates[i]
        w = (t - t0) / (t1 - t0)
        return z0 * (1 - w) + z1 * w

    def df(self, t: float) -> float:
        """Discount factor at maturity t (years) under continuous compounding."""
        if t <= 0:
            return 1.0
        z = self._zero_at(t)
        return math.exp(-z * t)

    # helpers to make curve bumps easy
    def bumped_parallel(self, dr: float) -> "ZeroCurve":
        return ZeroCurve(self.pillars[:], [z + dr for z in self.zero_rates])

    def bumped_key_index(self, idx: int, dr: float) -> "ZeroCurve":
        z = self.zero_rates[:]
        z[idx] = z[idx] + dr
        return ZeroCurve(self.pillars[:], z)
