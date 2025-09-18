from typing import Dict, List

from .curve import ZeroCurve


def dv01_curve(obj, curve: ZeroCurve, bp: float = 1.0) -> float:
    """Parallel DV01 using curve: PV change per 1bp move (units: currency per 1bp)."""
    dr = bp / 10000.0
    pv_up = obj.pv(curve=curve.bumped_parallel(+dr))
    pv_dn = obj.pv(curve=curve.bumped_parallel(-dr))
    return (pv_dn - pv_up) / 2.0


def effective_duration_curve(obj, curve: ZeroCurve, bp: float = 1.0) -> float:
    """Dimensionless effective duration from parallel curve bump."""
    dr = bp / 10000.0
    pv0 = obj.pv(curve=curve)
    pv_up = obj.pv(curve=curve.bumped_parallel(+dr))
    pv_dn = obj.pv(curve=curve.bumped_parallel(-dr))
    return -(pv_up - pv_dn) / (2 * pv0 * dr)


def keyrate_durations(
    obj, curve: ZeroCurve, key_indices: List[int], bp: float = 1.0
) -> Dict[float, float]:
    """
    Key-rate durations at selected curve pillar indices.
    Returns {tenor_years: duration}.
    MVP bump: nudge the zero at that pillar by ±bp and reprice.
    """
    dr = bp / 10000.0
    pv0 = obj.pv(curve=curve)
    krd = {}
    for idx in key_indices:
        c_up = curve.bumped_key_index(idx, +dr)
        c_dn = curve.bumped_key_index(idx, -dr)
        pv_up = obj.pv(curve=c_up)
        pv_dn = obj.pv(curve=c_dn)
        d = -(pv_up - pv_dn) / (2 * pv0 * dr)
        krd[curve.pillars[idx]] = d
    return krd


def keyrate_dv01s(
    obj, curve: ZeroCurve, key_indices: List[int], bp: float = 1.0
) -> Dict[float, float]:
    """
    Key-rate DV01s (KR01s): dollar PV change per 1bp bump at selected pillar indices.
    Works even when PV0 == 0 (e.g., par swaps), unlike keyrate_durations which normalizes by PV.
    Returns {tenor_years: dv01_per_1bp}.
    """
    dr = bp / 10000.0
    kr01 = {}
    for idx in key_indices:
        c_up = curve.bumped_key_index(idx, +dr)
        c_dn = curve.bumped_key_index(idx, -dr)
        pv_up = obj.pv(curve=c_up)
        pv_dn = obj.pv(curve=c_dn)
        dv01 = (pv_dn - pv_up) / 2.0
        kr01[curve.pillars[idx]] = dv01
    return kr01
