"""Classical relative trajectories for an illustrative repulsive pair potential.

Dimensionless coordinates use a length a, reduced mass mu, and speed v0.
The potential is U/(mu*v0**2) = 0.5 / rho**power. This is the short-range
repulsive part of a model interaction, not the Bronshten atom-air fit.
"""
import numpy as np
from scipy.integrate import solve_ivp


def trajectory(speed=1., impact=1.1, power=12, samples=600):
    def rhs(time, state):
        r = state[:2]
        force = .5 * power * r / np.linalg.norm(r)**(power + 2)
        return np.r_[state[2:], force]

    def exit_region(time, state):
        return np.linalg.norm(state[:2]) - 9.

    exit_region.direction = 1
    exit_region.terminal = True
    solution = solve_ivp(rhs, [0., 40. / speed], [-8., impact, speed, 0.],
                         rtol=1e-10, atol=1e-12, max_step=.025,
                         events=exit_region, dense_output=True)
    if not solution.success or not len(solution.t_events[0]):
        raise RuntimeError('Scattering trajectory did not leave the interaction region')
    times = np.linspace(0., solution.t[-1], samples)
    state = solution.sol(times).T
    radii = np.linalg.norm(state[:, :2], axis=1)
    force = .5 * power * state[:, :2] / radii[:, None]**(power + 2)
    energy = .5 * np.sum(state[:, 2:]**2, axis=1) + .5 / radii**power
    angular_momentum = state[:, 0] * state[:, 3] - state[:, 1] * state[:, 2]
    angle = np.arctan2(state[-1, 3], state[-1, 2])
    return dict(time=times, state=state, force=force, energy=energy,
                angular_momentum=angular_momentum, angle=angle)
