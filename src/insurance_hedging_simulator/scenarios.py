# src/insurance_hedging_simulator/scenarios.py
from typing import List, Literal, Optional
import math
import numpy as np
from .curve import ZeroCurve

# ---------- Parametric curve shapes ----------

def make_parametric_curve(
    pillars: List[float],
    base: float,
    slope: float = 0.0,
) -> ZeroCurve:
    """
    Build a simple parametric zero curve:
    z(t) = base + slope * (t / max(pillar)), continuous-compounded.
    slope > 0 => upward, slope < 0 => inverted, slope = 0 => flat.
    """
    max_t = max(pillars) if pillars else 1.0
    zeros = [base + slope * (t / max_t) for t in pillars]
    return ZeroCurve(pillars, zeros)

def make_curve(
    shape: Literal["flat", "upward", "inverted"],
    pillars: List[float],
    base: float = 0.03,
    slope: float = 0.01,
) -> ZeroCurve:
    if shape == "flat":
        s = 0.0
    elif shape == "upward":
        s = abs(slope)
    elif shape == "inverted":
        s = -abs(slope)
    else:
        raise ValueError("shape must be 'flat', 'upward', or 'inverted'")
    return make_parametric_curve(pillars, base, s)

# ---------- Vasicek short-rate model ----------

def vasicek_paths(
    r0: float,
    kappa: float,
    theta: float,
    sigma: float,
    dt: float,
    n_steps: int,
    n_paths: int,
    seed: Optional[int] = None,
) -> np.ndarray:
    """
    Euler-discretized Vasicek: dr = kappa*(theta - r)*dt + sigma*dW
    Returns array shape (n_paths, n_steps+1) including initial r0.
    """
    rng = np.random.default_rng(seed)
    r = np.empty((n_paths, n_steps + 1), dtype=float)
    r[:, 0] = r0
    sqrt_dt = math.sqrt(dt)
    for t in range(n_steps):
        z = rng.standard_normal(n_paths)
        r[:, t + 1] = r[:, t] + kappa * (theta - r[:, t]) * dt + sigma * sqrt_dt * z
    return r

def vasicek_zero_curve(
    rt: float,
    kappa: float,
    theta: float,
    sigma: float,
    pillars: List[float],
) -> ZeroCurve:
    """
    Build a zero curve from current short rate r_t using Vasicek closed-form ZCB price:
    P(0,T) = exp(A(T) - B(T)*r_t), z(T) = -ln P / T
    """
    zeros: List[float] = []
    for T in pillars:
        if T <= 0:
            zeros.append(0.0)
            continue
        B = (1.0 - math.exp(-kappa * T)) / kappa
        A = (theta - (sigma * sigma) / (2.0 * kappa * kappa)) * (B - T) - (sigma * sigma) * B * B / (4.0 * kappa)
        P = math.exp(A - B * rt)
        z = -math.log(P) / T
        zeros.append(z)
    return ZeroCurve(pillars, zeros)

def generate_vasicek_scenarios(
    r0: float,
    kappa: float,
    theta: float,
    sigma: float,
    dt: float,
    n_steps: int,
    n_paths: int,
    pillars: List[float],
    seed: Optional[int] = None,
):
    """
    Generate Monte Carlo short-rate paths and corresponding zero curves at each step.
    Returns:
      {
        "short_rate_paths": np.ndarray (n_paths, n_steps+1),
        "curves": List[List[ZeroCurve]] with shape [n_paths][n_steps+1]
      }
    """
    paths = vasicek_paths(r0, kappa, theta, sigma, dt, n_steps, n_paths, seed)
    curves = [
        [vasicek_zero_curve(rt, kappa, theta, sigma, pillars) for rt in paths[i]]
        for i in range(n_paths)
    ]
    return {"short_rate_paths": paths, "curves": curves}
