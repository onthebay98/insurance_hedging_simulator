from typing import List, Dict, Tuple, Union
from .curve import ZeroCurve
from .hedge_swap import SizedSwap, swap_pv_payer_fixed

# A hedge can be nothing, one swap, or a portfolio of swaps
HedgeType = Union[None, SizedSwap, List[SizedSwap]]

def shock_parallel_bp(curve: ZeroCurve, bp: float) -> ZeroCurve:
    """Return a curve bumped in parallel by bp basis points."""
    dr = bp / 10000.0
    return curve.bumped_parallel(dr)

def shock_keyrate_bp(curve: ZeroCurve, key_index: int, bp: float) -> ZeroCurve:
    """Return a curve bumped only at a single pillar by bp basis points."""
    dr = bp / 10000.0
    return curve.bumped_key_index(key_index, dr)

def _pv_swap_any(curve: ZeroCurve, hedge: HedgeType) -> float:
    """Compute PV for a hedge that may be None, a single swap, or a list of swaps."""
    if hedge is None:
        return 0.0
    if isinstance(hedge, list):
        total = 0.0
        for h in hedge:
            pv = swap_pv_payer_fixed(
                curve, h.notional, h.maturity_years, h.payments_per_year, h.fixed_rate
            )
            total += pv if h.pay_fixed else -pv
        return total
    # single SizedSwap
    pv = swap_pv_payer_fixed(
        curve, hedge.notional, hedge.maturity_years, hedge.payments_per_year, hedge.fixed_rate
    )
    return pv if hedge.pay_fixed else -pv

def run_stresses_on_liability_and_hedge(
    liability_obj,
    base_curve: ZeroCurve,
    sized_swap: HedgeType,   # None | SizedSwap | List[SizedSwap]
    shocks: List[Tuple[str, ZeroCurve]],
) -> List[Dict]:
    """
    Compute P&L under a list of curve shocks.
    Returns rows with shock name, liability P&L, hedge P&L, and net P&L.
    """
    rows = []
    pv_liab_base  = liability_obj.pv(curve=base_curve)
    pv_hedge_base = _pv_swap_any(base_curve, sized_swap)

    for name, shocked in shocks:
        pv_liab_sh  = liability_obj.pv(curve=shocked)
        pv_hedge_sh = _pv_swap_any(shocked, sized_swap)
        pnl_liab  = pv_liab_sh  - pv_liab_base
        pnl_hedge = pv_hedge_sh - pv_hedge_base
        rows.append({
            "shock": name,
            "liability_pnl": pnl_liab,
            "hedge_pnl": pnl_hedge,
            "net_pnl": pnl_liab + pnl_hedge,
        })
    return rows
