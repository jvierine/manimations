"""Dimant & Oppenheim (2017), Eqs. 45-48: a standalone density function.

z and r are in units of the ablated-neutral mean free path; z>0 is behind
the meteor. Return n_e/n_star, assuming n_e = n_i, where
n_star = 8*pi*r_M**2*n0*nA*(1+m/mA)*Gion/(sqrt(3)*lambda_T).
Multiply the result by n_star to obtain electron density in m^-3.
Reference: https://doi.org/10.1002/2017JA023963
"""
import numpy as np
from scipy.integrate import quad
from scipy.special import erf

# Related MetAblate implementation (upstream snapshot c31ef4e):
# https://github.com/danielk333/ablate/blob/c31ef4e67c58d477391ec499ca8dd73976be5e3d/src/metablate/models/dimant_oppenheim_2017.py
# This standalone version takes one point and returns ne/n_star, rather than
# a grid morphology or a density scaled with supplied meteor parameters.
# It combines the two Eq. 48 integrals into one quad call, integrates to 1,
# uses the analytic zero-width limit on the axis, and does not apply abs().
# Eq. 46 uses sqrt(1 + A/(2*pi)); that snapshot incorrectly used
# sqrt((1 + A)/(2*pi)) and moved the lower integration bound near the axis.
# The corresponding MetAblate fixes are in https://github.com/jvierine/ablate/pull/1.

def shape_components(R, cos_theta):
    """Return the three weighted, dimensionless Eq. 45 terms in H.

    R means s=physical radius/lambda_T here; cos_theta is the SPATIAL
    polar cosine (not the recoil cosine called mu earlier in the paper).
    Terms are |cos(theta)| f1, cos(theta) f2, f3. These are algebraic
    contributions to one ion population, not three particle populations.
    Eq. 46 is an interpolation; Eq. 48 uses the Eq. 9 trajectory approximation.
    """
    if R <= 0 or abs(cos_theta) > 1:
        raise ValueError('Use s > 0 and a spatial cosine between -1 and 1')
    c = abs(cos_theta)
    q = R ** (2 / 3)
    f1 = np.sqrt(2 * np.pi / 3) / R * erf(np.sqrt(1.5) * (R * c) ** (1 / 3))
    f1 -= np.exp(-1.5 * q * c ** (2 / 3)) * (
        (4 - np.pi) * c / (2 * np.sqrt(1 + (4 - np.pi)**2 * q * c**(2 / 3) / (2 * np.pi)))
        + 2 * c ** (1 / 3) / q)
    f2 = np.sqrt(2 * np.pi / 3) / R * erf(np.sqrt(1.5 * q)) - (1 + 2 / q) * np.exp(-1.5 * q)

    # Eq. 48: combine the two integrals; quad handles the integrable endpoint.
    def integrand(xi):
        kernel = np.sqrt(1 + 2 * q * xi ** (2 / 3) / np.pi) * np.exp(-1.5 * q * xi ** (2 / 3))
        angle = np.arcsin(np.clip(c * np.sqrt(1 - xi**2) / (xi * np.sqrt(1 - c**2)), 0, 1))
        return kernel * (np.sqrt(max(0, xi**2 - c**2) / (1 - xi**2)) + c * angle)

    f3 = quad(integrand, c, 1, epsabs=1e-8)[0] if c < 1 else 0.0
    return c * f1, cos_theta * f2, f3


def electron_density(z, r):
    R = np.hypot(z, r)
    if R == 0:
        return np.nan  # The point-source model is undefined at the meteor.
    return sum(shape_components(R, z / R)) / R
