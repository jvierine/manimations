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


def test_surface_flux_and_published_do_prefactor_reduce_to_q_normalization():
    # Part 1 Eq. 18 uses the OUTGOING surface density n0. Its half-normal
    # mean speed is sqrt(2/pi)*VT; using full-Maxwellian effusion gives a factor 2 error.
    from scipy.integrate import quad
    from scipy.constants import Boltzmann
    for temperature,speed,air_density,radius,beta in [(1800.,2e4,1e19,5e-5,.2),(2500.,7e4,4e18,5e-4,.7)]:
        vt=np.sqrt(Boltzmann*temperature/(28.085*atomic_mass))
        mean=quad(lambda x:x*np.sqrt(2/np.pi)*np.exp(-x*x/2),0,np.inf)[0]*vt
        np.testing.assert_allclose(mean,np.sqrt(2/np.pi)*vt)
        n0=1e20; sigma=5.61e-19*(speed/1000)**(-.8)
        length=vt/(air_density*sigma*speed);ma=29*atomic_mass;ms=28.085*atomic_mass
        rate=4*np.pi*radius**2*n0*mean
        # Dimant--Oppenheim Part 2 Eq. 45, with F=H/(R/lambda_T).
        published=8*np.pi*radius**2*n0*air_density*(beta*sigma/(4*np.pi))*(1+ms/ma)/(np.sqrt(3)*length)
        np.testing.assert_allclose(source_quantities(rate*ms,speed,beta,length,ma)[2],published,rtol=1e-12)


def test_native_gallery_matches_python_and_physical_surface_level():
    with h5py.File(ROOT/'data.h5') as f:
        for z,r,value in f['gallery/checks'][:]:
            np.testing.assert_allclose(value,electron_density(z,r),rtol=2e-7)
        for t,r in zip(f['gallery/theta'][::8],f['gallery/radius'][::8]):
            np.testing.assert_allclose(electron_density(r*np.cos(t),r*np.sin(t)),.05,rtol=2e-7)
        length=f.attrs['density_100km_lambda_m']
        n=f.attrs['density_100km_number_density']
        np.testing.assert_allclose(length,collision_lengths(50000.,2000.,n)[1])


def test_shape_terms_match_independent_path_weight_and_front_back_difference():
    # Part 2 Eqs. 25, 40--41: the signed term is the finite-leg source
    # integral. Check it independently of the closed-form erf evaluation.
    from scipy.integrate import quad
    from meteor_rcs.do_density import shape_components
    for radius in [.1, 1., 3., 10.]:
        weight=lambda eta:(1+(radius*eta)**(2/3))*np.exp(-1.5*(radius*eta)**(2/3))
        finite_leg=quad(weight, 0., 1., epsabs=1e-11)[0]
        for cosine in [.2, .5, 1.]:
            behind=np.array(shape_components(radius, cosine))
            front=np.array(shape_components(radius, -cosine))
            np.testing.assert_allclose(behind[1], cosine*finite_leg, rtol=1e-9)
            np.testing.assert_allclose(behind[[0,2]],front[[0,2]])
            np.testing.assert_allclose(behind.sum()-front.sum(),2*cosine*finite_leg,rtol=1e-10)
            assert front.sum()>0
        # The partial-azimuth region disappears on the axis; only f3 remains
        # at a right angle to the trajectory. These are geometrical limits.
        assert shape_components(radius, 1.)[2]==0.
        np.testing.assert_array_equal(shape_components(radius, 0.)[:2],[0.,0.])


def test_angular_access_boundary_follows_recoil_geometry():
    # The allowed-azimuth interval switches from all/none to partial at
    # xi=abs(cos theta), since B^2-A^2=xi^2-cos(theta)^2.
    for cosine in [-.8,-.3,.3,.8]:
        for xi in [.1,.5,.95]:
            a=np.sqrt(1-xi**2)*cosine
            b=xi*np.sqrt(1-cosine**2)
            np.testing.assert_allclose(b*b-a*a,xi*xi-cosine*cosine)
            crosses_zero=(a-b<0<a+b)
            assert crosses_zero==(xi>abs(cosine))


def test_regrouped_shape_integral_matches_direct_allowed_ray_sum():
    # Independently check the regrouping in Part 2 Eq. 25, including the
    # azimuth factor 1/2, against a direct angular sum. Smooth synthetic ray
    # weights isolate this geometry from the paper's f1/J approximations.
    from scipy.integrate import quad
    nodes,weights=np.polynomial.legendre.leggauss(160)
    phi_nodes,phi_weights=np.polynomial.legendre.leggauss(512)
    phi=np.pi*(phi_nodes+1)
    for chi in [-.7,.3,.7]:
        c=abs(chi)
        jinfty=lambda xi:np.exp(-xi)*(1+.3/xi)
        jr=lambda xi:.4*(1-xi)*jinfty(xi)
        direct=0.
        cut=np.arcsin(c)
        for lower,upper in [(0.,cut),(cut,np.pi/2)]:
            theta=lower+(nodes+1)*(upper-lower)/2
            xi=np.sin(theta)
            for sign in [-1,1]:
                kappa=sign*np.cos(theta[:,None])*chi+xi[:,None]*np.sqrt(1-chi*chi)*np.cos(phi)
                angular=.5*np.pi*(np.maximum(kappa,0)@phi_weights)
                path=jinfty(xi)+sign*jr(xi)
                direct+=(upper-lower)/2*np.dot(weights,xi*path*angular)
        f1=quad(lambda xi:jinfty(xi)*xi,0.,c)[0]
        f2=quad(lambda xi:jr(xi)*xi,0.,1.)[0]
        def partial(xi):
            angle=np.arcsin(np.clip(c*np.sqrt(1-xi*xi)/(xi*np.sqrt(1-c*c)),0,1))
            k=np.sqrt((xi*xi-c*c)/(1-xi*xi))+c*angle
            return 2/np.pi*jinfty(xi)*xi*k
        f3=quad(partial,c,1.,epsabs=1e-10)[0]
        np.testing.assert_allclose(direct,np.pi*(c*f1+chi*f2+f3),rtol=3e-5)


def test_cut_faces_sample_the_actual_density_inside_the_isosurface():
    # The new coloured faces are physical meridional sections. Check their
    # saved native densities against independent Python quadrature and the
    # outer contour, including both axial ends and the transverse direction.
    with h5py.File(ROOT/'data.h5') as f:
        theta=f['gallery/theta'][:]
        radii=f['gallery/cut_radius'][:].reshape(len(theta),-1)
        density=f['gallery/cut_density'][:].reshape(radii.shape)
        np.testing.assert_allclose(radii[:,-1],f['gallery/radius'][:])
        np.testing.assert_allclose(density[:,-1],.05,rtol=2e-7)
        assert np.all(density[:,:-1]>=.05)
        for j in [0,18,36,54,72]:
            for k in [0,24,48,72,96]:
                r=radii[j,k];t=theta[j]
                np.testing.assert_allclose(density[j,k],electron_density(r*np.cos(t),r*np.sin(t)),rtol=2e-7)
