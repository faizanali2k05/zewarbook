"""Traditional Pakistani jewelry weight units and gold-rate math.

Authoritative conversions:
    1 tola  = 11.664 grams
    1 tola  = 12 masha
    1 masha = 8 rati  (so 1 tola = 96 rati)
    1 point = 0.01 tola (used in ledger entry as fractional tola)
"""
from dataclasses import dataclass

TOLA_IN_GRAMS = 11.664
MASHA_PER_TOLA = 12
RATI_PER_MASHA = 8
RATI_PER_TOLA = MASHA_PER_TOLA * RATI_PER_MASHA  # 96
POINT_PER_TOLA = 100  # 1 tola = 100 points


@dataclass(frozen=True)
class WeightBreakdown:
    """Whole-unit decomposition of a tola value (e.g. 1.5 tola = 1t 6m 0r)."""

    tola: int
    masha: int
    rati: float

    def as_str(self) -> str:
        return f"تولہ: {self.tola} | ماشہ: {self.masha} | رتی: {self.rati:.2f}"


def grams_to_tola(grams: float) -> float:
    return grams / TOLA_IN_GRAMS if grams else 0.0


def tola_to_grams(tola: float) -> float:
    return tola * TOLA_IN_GRAMS


def tola_to_masha(tola: float) -> float:
    return tola * MASHA_PER_TOLA


def masha_to_tola(masha: float) -> float:
    return masha / MASHA_PER_TOLA


def tola_to_rati(tola: float) -> float:
    return tola * RATI_PER_TOLA


def rati_to_tola(rati: float) -> float:
    return rati / RATI_PER_TOLA


def point_to_tola(point: float) -> float:
    return point / POINT_PER_TOLA


def tola_to_point(tola: float) -> float:
    return tola * POINT_PER_TOLA


def decompose(tola_value: float) -> WeightBreakdown:
    """Split a fractional tola into (whole tola, whole masha, fractional rati)."""
    if not tola_value:
        return WeightBreakdown(0, 0, 0.0)
    tola_whole = int(tola_value)
    masha_value = (tola_value - tola_whole) * MASHA_PER_TOLA
    masha_whole = int(masha_value)
    rati_value = (masha_value - masha_whole) * RATI_PER_MASHA
    return WeightBreakdown(tola_whole, masha_whole, round(rati_value, 2))


def rate_per_gram_from_tola(rate_per_tola: float) -> float:
    return rate_per_tola / TOLA_IN_GRAMS if rate_per_tola else 0.0


def rate_per_tola_from_gram(rate_per_gram: float) -> float:
    return rate_per_gram * TOLA_IN_GRAMS if rate_per_gram else 0.0


def price_from_grams(grams: float, rate_per_tola: float) -> float:
    """(grams / 11.664) × rate_per_tola"""
    if not grams or not rate_per_tola:
        return 0.0
    return (grams / TOLA_IN_GRAMS) * rate_per_tola


def price_from_tola(tola: float, point: float, rate_per_tola: float) -> float:
    """(tola + point/100) × rate_per_tola"""
    if not rate_per_tola:
        return 0.0
    weight_tola = tola + point_to_tola(point)
    return weight_tola * rate_per_tola
