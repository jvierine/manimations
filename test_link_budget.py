"""Numerical checks for the executable link-budget lecture."""
import unittest
import numpy as np
from link_budget import bpsk_ber, simulate_bpsk, example_budget


class LinkBudgetChecks(unittest.TestCase):
    def test_ber_matches_gaussian_theory(self):
        for db in [0, 2, 4, 6, 8]:
            bits, _, _, decoded = simulate_bpsk(db)
            expected = float(bpsk_ber(db))
            observed = np.mean(bits != decoded)
            sigma = np.sqrt(expected * (1 - expected) / len(bits))
            self.assertLess(abs(observed - expected), 5 * sigma)

    def test_complex_noise_normalization(self):
        bits, symbols, samples, decoded = simulate_bpsk(0)
        noise = samples - symbols
        self.assertAlmostEqual(noise.real.var(), .5, delta=.004)
        self.assertAlmostEqual(noise.imag.var(), .5, delta=.004)
        np.testing.assert_array_equal(decoded, samples.real >= 0)

    def test_stream_contains_errors_and_correct_decisions(self):
        bits, _, _, decoded = simulate_bpsk(0, count=24, seed=8)
        self.assertTrue(np.any(bits != decoded))
        self.assertTrue(np.any(bits == decoded))

    def test_budget(self):
        b = example_budget()
        self.assertAlmostEqual(b["fspl"], 170.9333689431, places=8)
        self.assertAlmostEqual(b["pr_dbw"], -134.2493873661, places=8)
        self.assertAlmostEqual(float(bpsk_ber(b["required_db"])), 1e-5, places=12)
        self.assertAlmostEqual(b["margin_db"], 2.0010088697, places=8)


if __name__ == "__main__":
    unittest.main()
