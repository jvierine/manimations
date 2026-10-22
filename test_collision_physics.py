"""Check conservation and similarity for the lecture's elastic encounter model."""
import numpy as np
from meteor_rcs.collision_physics import trajectory


def test_relative_trajectory_conserves_energy_and_angular_momentum():
    for speed in [1., 2.]:
        result = trajectory(speed)
        for name in ['energy', 'angular_momentum']:
            values = result[name]
            assert np.max(np.abs(values / values[0] - 1.)) < 2e-8


def test_faster_encounter_is_less_deflected_at_fixed_impact_parameter():
    slow, fast = trajectory(1.), trajectory(2.)
    assert 0 < fast['angle'] < slow['angle']
    assert fast['time'][-1] < slow['time'][-1]


def test_inverse_power_scattering_has_the_derived_speed_similarity():
    # Doubling speed requires b -> b*2^(-2/s) to preserve the dimensionless
    # scattering trajectory; area then scales as speed^(-4/s).
    for power in [5, 12]:
        slow = trajectory(1., 1.1, power)
        fast = trajectory(2., 1.1 * 2**(-2/power), power)
        # The launch/exit radii are finite, rather than infinity.
        assert np.isclose(slow['angle'], fast['angle'], rtol=3e-4)
