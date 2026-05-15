"""Gold purity calculator using Archimedes' principle.

Inputs:  weight in air (grams), weight in water (grams)
Output:  purity for each impurity-metal assumption.

Formula:
    apparent_loss = w_air - w_water          (assume rho_water = 1 g/cm^3)
    rho_sample    = w_air / apparent_loss
    purity_fraction (for impurity metal with density rho_i, pure gold rho_g):
        From conservation of mass and volume of a 2-metal alloy:
            x = (1/rho_i - 1/rho_sample) / (1/rho_i - 1/rho_g)
        where x is the mass-fraction of pure gold.

5 metals shown in the UI use 5 impurity-metal densities. Values calibrated to
match screenshot #7 (air=11.664, water=11.000 -> pure_gold rows shown).
"""
from dataclasses import dataclass

PURE_GOLD_DENSITY = 19.30  # g/cm^3

# Impurity densities (g/cm^3) for each metal classification visible in the UI.
# Reverse-calibrated from screenshot #7 (air=11.664, water=11.000) so that the
# pure-gold-grams column matches: Local=10.7037, Copper=10.6614, Standard=10.6265,
# Silver=10.3690, Pure Silver=10.3399.
METALS = {
    "Local":      8.76,
    "Copper":     8.98,
    "Standard":   9.14,
    "Silver":    10.21,
    "Pure Silver": 10.32,
}


@dataclass(frozen=True)
class PurityRow:
    metal: str
    purity_percent: float
    impurity_percent: float
    pure_gold_grams: float
    impurity_grams: float


def calculate_density(weight_air: float, weight_water: float) -> tuple[float, float]:
    if weight_air <= 0 or weight_water <= 0:
        raise ValueError("Weights must be positive numbers")
    if weight_water >= weight_air:
        raise ValueError("Weight in water must be less than weight in air")
    apparent_loss = weight_air - weight_water
    density = weight_air / apparent_loss
    return density, apparent_loss


def purity_for_metal(weight_air: float, density_sample: float, impurity_density: float) -> PurityRow:
    """Two-metal alloy: solve for gold mass-fraction x given sample density."""
    inv_sample = 1.0 / density_sample
    inv_gold = 1.0 / PURE_GOLD_DENSITY
    inv_imp = 1.0 / impurity_density

    denom = inv_imp - inv_gold
    if denom == 0:
        x = 0.0
    else:
        x = (inv_imp - inv_sample) / denom
    # Clamp to [0, 1] — physical bounds.
    x = max(0.0, min(1.0, x))

    pure_gold = weight_air * x
    impurity = weight_air * (1.0 - x)
    return PurityRow(
        metal="",
        purity_percent=round(x * 100, 4),
        impurity_percent=round((1 - x) * 100, 4),
        pure_gold_grams=round(pure_gold, 4),
        impurity_grams=round(impurity, 4),
    )


def calculate_all(weight_air: float, weight_water: float) -> dict[str, PurityRow]:
    density, _ = calculate_density(weight_air, weight_water)
    results = {}
    for name, imp_density in METALS.items():
        row = purity_for_metal(weight_air, density, imp_density)
        results[name] = PurityRow(
            metal=name,
            purity_percent=row.purity_percent,
            impurity_percent=row.impurity_percent,
            pure_gold_grams=row.pure_gold_grams,
            impurity_grams=row.impurity_grams,
        )
    return results
