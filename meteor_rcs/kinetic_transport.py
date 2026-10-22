"""Transparent teaching examples for force-free ion transport.

The one-dimensional source slab is an explanatory constant-area, single-speed
stream. It is not a quantitative Dimant--Oppenheim meteor-cloud prediction.
"""
import numpy as np


def backtrace(position, velocity, lookback):
    """Earlier positions on one constant-velocity characteristic; all SI units."""
    return np.asarray(position) - np.asarray(lookback)[..., None] * np.asarray(velocity)


def slab_density(position, speed, production_rate, start=0., stop=1.):
    """Steady n [m^-3] from Q [m^-3 s^-1], v [m/s], x [m]; zero upstream."""
    if speed <= 0 or stop <= start:
        raise ValueError('Use a positive speed and a slab of positive thickness')
    travelled = np.clip(np.asarray(position) - start, 0., stop - start)
    return production_rate * travelled / speed


def velocity_wedge_volume(speed, thickness, solid_angle):
    """Exact velocity-space volume [(m/s)^3] of a spherical shell wedge."""
    if speed < 0 or thickness < 0 or not 0 <= solid_angle <= 4*np.pi:
        raise ValueError('Invalid speed, shell thickness, or solid angle')
    return solid_angle * ((speed + thickness)**3 - speed**3) / 3.
