"""SI and normalization checks for the meteor presentation's interfaces."""
import h5py
import numpy as np
from scipy.constants import atomic_mass

from meteor_rcs.prepare_assets import ROOT, source_quantities, collision_lengths
from meteor_rcs.do_density import electron_density
from meteor_head_rcs import MeteorHeadRCS, boost_photon


def test_source_units_and_line_density():
    production,q,nstar=source_quantities(28.085*atomic_mass*1e15,5e4,.5,.1,29*atomic_mass)
    np.testing.assert_allclose(production,5e14)
    np.testing.assert_allclose(q,1e10)
    np.testing.assert_allclose(nstar,1e10*(1+28.085/29)/(2*np.sqrt(6*np.pi)*.1**2))


def test_archived_ablation_normalization():
    with h5py.File(ROOT/'data.h5') as f:
        q=f['trajectory/q_m1'][:]
        np.testing.assert_allclose(q*f['trajectory/velocity_m_s'][:],f['trajectory/electron_production_s1'][:])
        assert 3.5e13<f.attrs['critical_density_m3']<3.6e13


def test_do_axis_and_scaling():
    assert electron_density(1,0)>electron_density(-1,0)>0
    assert np.isnan(electron_density(0,0))
    np.testing.assert_allclose(electron_density(1,.5),electron_density(1,-.5))


def test_kepler_perihelion_and_closed_laps():
    a=2.2;e=1-1/a
    for m in [0,6*np.pi,-6*np.pi]:
        np.testing.assert_allclose(MeteorHeadRCS.kepler_position(m,a,e),[1,0,0],atol=1e-12)


def test_mean_free_path_frames_and_speed_scaling():
    from scipy.constants import Boltzmann
    speeds=np.array([1e4,8e4])
    atmosphere,thermal=collision_lengths(speeds,2000.,1e19)
    vt=np.sqrt(Boltzmann*2000/(28.085*atomic_mass))
    np.testing.assert_allclose(thermal/atmosphere,vt/speeds)
    np.testing.assert_allclose(thermal[1]/thermal[0],8**(-.2))
    np.testing.assert_allclose(atmosphere[1]/atmosphere[0],8**.8)


def test_density_rescaling_preserves_shape_and_changes_amplitude():
    def density(z,r,q,length):
        nstar=source_quantities(28.085*atomic_mass*q*5e4,5e4,1.,length,29*atomic_mass)[2]
        return nstar*electron_density(z/length,r/length)
    base=density(.3,.15,1e12,.1)
    np.testing.assert_allclose(density(.3,.15,2e12,.1),2*base)
    np.testing.assert_allclose(density(.6,.3,1e12,.2),base/4)


def test_isotropic_photons_carry_forward_momentum_in_sun_frame():
    # Six equal-energy photons in opposite directions have zero momentum in
    # the grain frame. Their boosted total must obey p_x*c / E = v/c.
    beta=.3
    rays=[boost_photon(sign*axis,beta) for axis in np.eye(3) for sign in [-1,1]]
    energies=np.array([energy for _,energy in rays])
    directions=np.array([direction for direction,_ in rays])
    np.testing.assert_allclose(np.linalg.norm(directions,axis=1),1.)
    np.testing.assert_allclose((energies[:,None]*directions).sum(axis=0)/energies.sum(),[beta,0,0],atol=1e-15)
    for direction,energy in rays:
        restored,ratio=boost_photon(direction,-beta)
        assert np.isclose(np.linalg.norm(restored),1.)
        np.testing.assert_allclose(energy*ratio,1.)
