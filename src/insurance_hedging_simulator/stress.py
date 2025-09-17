from typing import List, Dict, Tuple
from .curve import ZeroCurve

def shock_parallel_bp(curve: ZeroCurve, bp: float) -> ZeroCurve:
    dr = bp / 10000.0
    return curve.bumped_parallel(dr)

def shock_keyrate_bp(curve: ZeroCurve, key_index: int, bp: float) -> ZeroCurve:
    dr = bp / 10000.0
    return curve.bumped_key_index(key_index, dr)

def run_stresses_on_liability_and_hedge(
    liability_obj,
    base_curve: ZeroCurve,
    sized_swap,     # SizedSwap or None
    shocks: List[Tuple[str, ZeroCurve]],
) -> List[Dict]:
    """
    Returns a list of rows with pre/post PV and P&L under each shocked curve.
    """
    rows = []
    pv_liab_base = liability_obj.pv(curve=base_curve)
    pv_swap_base = 0.0
    if sized_swap is not None:
        from .hedge_swap import swap_pv_payer_fixed
        pv_swap_base = swap_pv_payer_fixed(
            base_curve,
            sized_swap.notional,
            sized_swap.maturity_years,
            sized_swap.payments_per_year,
            sized_swap.fixed_rate,
        )
    for name, shocked in shocks:
        pv_liab_sh = liability_obj.pv(curve=shocked)
        pnl_liab = pv_liab_sh - pv_liab_base

        pnl_swap = 0.0
        if sized_swap is not None:
            pv_swap_sh = swap_pv_payer_fixed(
                shocked,
                sized_swap.notional,
                sized_swap.maturity_years,
                sized_swap.payments_per_year,
                sized_swap.fixed_rate,
            )
            pnl_swap = pv_swap_sh - pv_swap_base

        rows.append({
            "shock": name,
            "liability_pnl": pnl_liab,
            "hedge_pnl": pnl_swap,
            "net_pnl": pnl_liab + pnl_swap,
        })
    return rows
