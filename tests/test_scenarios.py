# tests/test_scenarios.py
import numpy as np
from math import isclose

from insurance_hedging_simulator.scenarios import (
    make_curve,
    vasicek_paths,
    vasicek_zero_curve,
    generate_vasicek_scenarios,
)
from insurance_hedging_simulator.liabilities import AnnuityCertain


def test_make_curve_shapes():
    pillars = [0.5, 1, 2, 5, 10, 30]

    flat = make_curve("flat", pillars, base=0.03, slope=0.01)
    assert all(isclose(z, 0.03, rel_tol=0, abs_tol=1e-12) for z in flat.zero_rates)

    up = make_curve("upward", pillars, base=0.03, slope=0.02)
    assert up.zero_rates[0] < up.zero_rates[-1]  # increasing term structure

    inv = make_curve("inverted", pillars, base=0.03, slope=0.02)
    assert inv.zero_rates[0] > inv.zero_rates[-1]  # decreasing term structure


def test_vasicek_paths_shape_and_seed():
    paths = vasicek_paths(
        r0=0.03, kappa=0.5, theta=0.03, sigma=0.01,
        dt=1/12, n_steps=12, n_paths=10, seed=123
    )
    assert paths.shape == (10, 13)
    # same seed => identical paths
    paths2 = vasicek_paths(
        r0=0.03, kappa=0.5, theta=0.03, sigma=0.01,
        dt=1/12, n_steps=12, n_paths=10, seed=123
    )
    assert np.allclose(paths, paths2)


def test_vasicek_zero_curve_flat_when_rt_eq_theta_and_sigma0():
    # With sigma=0 and r_t = theta, the Vasicek closed form reduces to z(T) = theta (flat curve)
    theta = 0.03
    curve = vasicek_zero_curve(
        rt=theta, kappa=0.5, theta=theta, sigma=0.0,
        pillars=[0.5, 1, 2, 5, 10, 30]
    )
    assert all(isclose(z, theta, rel_tol=0, abs_tol=1e-12) for z in curve.zero_rates)


def test_vasicek_mean_reversion_stat_sanity():
    # Start far from theta and check the *average* terminal rate drifts toward theta
    r0, theta, kappa, sigma = 0.06, 0.03, 1.0, 0.005
    paths = vasicek_paths(
        r0=r0, kappa=kappa, theta=theta, sigma=sigma,
        dt=1/12, n_steps=60, n_paths=500, seed=7  # ~5y horizon, 500 paths
    )
    terminal_mean = paths[:, -1].mean()
    assert abs(terminal_mean - theta) < 0.01  # within ~1% (10 bps) tolerance


def test_generate_vasicek_scenarios_shapes():
    pillars = [0.5, 1, 2, 5, 10]
    out = generate_vasicek_scenarios(
        r0=0.03, kappa=0.5, theta=0.03, sigma=0.01,
        dt=1/12, n_steps=6, n_paths=7, pillars=pillars, seed=1
    )
    paths = out["short_rate_paths"]
    curves = out["curves"]

    assert paths.shape == (7, 7)               # n_paths x (n_steps+1)
    assert len(curves) == 7                    # one list per path
    assert all(len(row) == 7 for row in curves)  # one curve per time step
    # Each curve row contains ZeroCurve objects with expected pillars
    assert all(curves[0][0].pillars == pillars for _ in range(1))


def test_flat_curve_parity_via_make_curve():
    # Flat curve PV should match flat-rate PV for the same rate
    r = 0.03
    pillars = [0.5, 1, 2, 5, 10, 30]
    curve = make_curve("flat", pillars, base=r, slope=0.01)  # slope ignored for "flat"
    ac = AnnuityCertain(payment=100.0, n_payments=20)
    assert isclose(ac.pv(r=r), ac.pv(curve=curve), rel_tol=1e-6)
