"""Quantify RJ's fractional overestimate of Planck spectral radiance.

Run: conda run -n base python rayleigh_jeans_accuracy.py
The exact ratio is B_RJ/B_P = expm1(x)/x, x = h*nu/(k_B*T).
Error is relative to Planck, not relative to the RJ approximation.
"""
import argparse
import math

H = 6.62607015e-34  # J s, exact SI
K_B = 1.380649e-23  # J/K, exact SI


def relative_error(frequency_hz, temperature_k):
    if temperature_k <= 0 or frequency_hz < 0:
        raise ValueError("Require T > 0 K and frequency >= 0 Hz")
    x = H * frequency_hz / (K_B * temperature_k)
    return math.expm1(x) / x - 1 if x else 0.0


def frequency_for_error(error, temperature_k=300.0):
    """Monotonic bisection for (B_RJ-B_P)/B_P = error."""
    if not 0 < error < 1 or temperature_k <= 0:
        raise ValueError("Require 0 < error < 1 and T > 0 K")
    lo, hi = 0.0, K_B * temperature_k / H * 2
    for _ in range(100):
        mid = (lo + hi) / 2
        if relative_error(mid, temperature_k) < error:
            lo = mid
        else:
            hi = mid
    return (lo + hi) / 2


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--temperature", type=float, default=300.0)
    args = parser.parse_args()
    print(f"T = {args.temperature:g} K; error = (B_RJ - B_P) / B_P")
    for tolerance in (0.001, 0.01, 0.05, 0.1):
        nu = frequency_for_error(tolerance, args.temperature)
        assert math.isclose(relative_error(nu, args.temperature), tolerance, abs_tol=1e-12)
        print(f"{100*tolerance:5g}% error: {nu/1e9:10.3f} GHz")
    for ghz in (10, 100, 300, 600, 1000):
        print(f"{ghz:5g} GHz: {100*relative_error(ghz*1e9, args.temperature):.4f}% error")
