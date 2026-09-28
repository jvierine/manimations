"""Off-slide Monte Carlo check. Run: conda run -n base python validate_bpsk.py.

Independent complex Gaussian noise; unit-energy BPSK symbols.
Save counts, predictions and binomial acceptance intervals in HDF5.
"""
from pathlib import Path
import h5py
import numpy as np
from scipy.stats import binom
from link_budget import bpsk_ber, simulate_bpsk


def main():
    levels = np.arange(-10., 11., 2.)
    count = 2_000_000
    seed = 20260928
    errors = []
    for index, level in enumerate(levels):
        wrong = 0
        for chunk in range(10):
            bits, _, _, decoded = simulate_bpsk(level, count=count // 10,
                                                seed=seed + 100 * index + chunk)
            wrong += np.count_nonzero(bits != decoded)
        errors.append(wrong)
    errors = np.asarray(errors)
    theory = bpsk_ber(levels)
    # Simultaneous check with a conservative per-point false-rejection probability.
    lower = binom.ppf(5e-7, count, theory)
    upper = binom.ppf(1 - 5e-7, count, theory)
    passed = (errors >= lower) & (errors <= upper)
    output = Path("media/link_budget/ber_validation.h5")
    output.parent.mkdir(parents=True, exist_ok=True)
    with h5py.File(output, "w") as h:
        for name, values in dict(ebn0_db=levels, errors=errors,
                                 bit_count=np.full(len(levels), count),
                                 measured_ber=errors / count, theoretical_ber=theory,
                                 lower_error_count=lower, upper_error_count=upper,
                                 passed=passed).items():
            h.create_dataset(name, data=values)
        h.attrs["seed"] = seed
        h.attrs["script"] = "validate_bpsk.py"
        h.attrs["per_point_acceptance_probability"] = 0.999999
    for db, observed, predicted in zip(levels, errors / count, theory):
        print(f"{db:+5.1f} dB: simulated {observed:.7g}, theory {predicted:.7g}")
    assert passed.all(), f"Failed levels: {levels[~passed]}"
    print(f"PASS: {len(levels)} levels, {count:,} bits per level. {output}")


if __name__ == "__main__":
    main()
