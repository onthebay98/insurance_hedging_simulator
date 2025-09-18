from typing import Protocol


class PVable(Protocol):
    def pv(self, r: float) -> float: ...


def effective_duration(obj: PVable, r: float, dr: float = 1e-4) -> float:
    pv0 = obj.pv(r)
    pv_up = obj.pv(r + dr)
    pv_dn = obj.pv(r - dr)
    return -(pv_up - pv_dn) / (2 * pv0 * dr)


def dv01(obj: PVable, r: float, bp: float = 1.0) -> float:
    dr = bp / 10000.0
    pv_up = obj.pv(r + dr)
    pv_dn = obj.pv(r - dr)
    return (pv_dn - pv_up) / 2.0
