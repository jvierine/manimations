"""Check the counting and characteristic examples used in the lecture."""
import numpy as np
from meteor_rcs.kinetic_transport import backtrace, slab_density, velocity_wedge_volume


def test_backtrace_reaches_the_observation_point_after_the_lookback_time():
    r = np.array([1., 2., 3.]); v = np.array([300., -400., 10.])
    time = np.array([0., .001, .002])
    assert np.allclose(backtrace(r, v, time) + time[:, None]*v, r)


def test_source_slab_satisfies_steady_transport_and_the_upstream_boundary():
    speed, rate = 1000., 1e10
    x = np.linspace(-.2, 1.2, 10001)
    n = slab_density(x, speed, rate)
    expected = np.where((x > 0) & (x < 1), rate, 0.)
    interior = (np.abs(x) > .001) & (np.abs(x-1) > .001)
    assert np.allclose(speed*np.gradient(n, x)[interior], expected[interior], atol=.1)
    assert n[0] == 0
    assert np.isclose(n[-1], 1e7)
    assert np.allclose(slab_density(x, 2*speed, rate), n/2)


def test_spherical_velocity_measure_is_the_thin_shell_limit():
    speed, thickness = 1000., .001
    omega = .02
    exact = velocity_wedge_volume(speed, thickness, omega)
    thin = speed**2 * thickness * omega
    assert np.isclose(exact, thin, rtol=2e-6)
    assert np.isclose(velocity_wedge_volume(0., speed, 4*np.pi), 4*np.pi*speed**3/3)


def test_recoil_animation_conserves_momentum_energy_and_com_shell():
    from meteor_rcs.kinetic_transport import cold_recoil
    speed = 50e3
    for ratio in [.25, 1., 3., 10.]:
        for angle in [0., .2, .7, 1.3]:
            ion, air = cold_recoil(speed, ratio, angle)
            incoming = np.array([speed, 0.])
            assert np.allclose(air + ratio*ion, incoming)
            assert np.isclose(air@air + ratio*(ion@ion), speed**2)
            center = incoming/(1+ratio)
            assert np.isclose(np.linalg.norm(ion-center), np.linalg.norm(center))
