import unittest

from src.domain import purity, units


class UnitConversionTests(unittest.TestCase):
    def test_one_tola_is_11p664_grams(self):
        self.assertAlmostEqual(units.tola_to_grams(1), 11.664, places=4)
        self.assertAlmostEqual(units.grams_to_tola(11.664), 1.0, places=4)

    def test_tola_to_masha_multiplies(self):
        self.assertEqual(units.tola_to_masha(1), 12)
        self.assertEqual(units.masha_to_tola(12), 1)

    def test_tola_to_rati_multiplies(self):
        self.assertEqual(units.tola_to_rati(1), 96)
        self.assertEqual(units.rati_to_tola(96), 1)

    def test_point_to_tola(self):
        self.assertAlmostEqual(units.point_to_tola(100), 1.0)
        self.assertAlmostEqual(units.tola_to_point(0.5), 50)

    def test_decompose_returns_whole_tola_masha_fractional_rati(self):
        # 11.000g / 11.664 ≈ 0.9431 tola → 0 tola, 11 masha, ~2.54 rati
        bd = units.decompose(units.grams_to_tola(11.0))
        self.assertEqual(bd.tola, 0)
        self.assertEqual(bd.masha, 11)
        self.assertAlmostEqual(bd.rati, 2.54, delta=0.05)

    def test_price_from_grams(self):
        # 11.664g at 9000/tola = 9000 rupees
        self.assertAlmostEqual(units.price_from_grams(11.664, 9000), 9000, places=2)

    def test_rate_per_gram_from_tola(self):
        # 9000 / 11.664 ≈ 771.6
        self.assertAlmostEqual(units.rate_per_gram_from_tola(9000), 771.6, places=1)


class PurityTests(unittest.TestCase):
    def test_air_must_exceed_water(self):
        with self.assertRaises(ValueError):
            purity.calculate_density(10, 10)
        with self.assertRaises(ValueError):
            purity.calculate_density(10, 11)

    def test_pure_gold_yields_100_percent(self):
        # If sample density == gold density, copper-impurity row must show ~100%
        air = 19.30
        water = 18.30  # apparent_loss=1 → density=19.30 (pure gold)
        rows = purity.calculate_all(air, water)
        self.assertGreater(rows["Copper"].purity_percent, 99.0)

    def test_all_five_metals_present(self):
        rows = purity.calculate_all(11.664, 11.0)
        self.assertEqual(set(rows.keys()),
                         {"Local", "Copper", "Standard", "Silver", "Pure Silver"})
        for row in rows.values():
            self.assertGreater(row.pure_gold_grams, 0)
            self.assertLess(row.pure_gold_grams, 11.664)

    def test_lower_impurity_density_gives_higher_purity(self):
        # 8.40 (Local) < 8.96 (Copper), so for same sample,
        # Local row reports higher pure-gold mass than Copper.
        rows = purity.calculate_all(11.664, 11.0)
        self.assertGreater(rows["Local"].pure_gold_grams,
                           rows["Copper"].pure_gold_grams)


if __name__ == "__main__":
    unittest.main()
