import math
from math import isclose
from insurance_hedging_simulator.curve import ZeroCurve

def test_df_trivial_t0_is_one():
    curve = ZeroCurve([1, 2], [0.03, 0.04])
    assert curve.df(0.0) == 1.0
    assert curve.df(-1.0) == 1.0

def test_df_endpoint_behavior_and_interpolation():
    pillars = [0.5, 1, 2, 5]
    zeros   = [0.030, 0.031, 0.033, 0.036]
    curve = ZeroCurve(pillars, zeros)

    # below first pillar → uses first zero
    assert isclose(curve._zero_at(0.25), zeros[0], rel_tol=1e-12)
    # above last pillar → uses last zero
    assert isclose(curve._zero_at(10.0), zeros[-1], rel_tol=1e-12)
    # interpolate inside [1,2]
    z_mid = curve._zero_at(1.5)
    assert zeros[1] < z_mid < zeros[2]

    # DF uses exp(-z * t) with continuous comp
    t = 1.5
    z = curve._zero_at(t)
    assert isclose(curve.df(t), math.exp(-z * t), rel_tol=1e-12)
