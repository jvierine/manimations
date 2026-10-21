"""Prepare small, reproducible slide figures; never launch an EM calculation.

The bundled inputs.h5 contains an archived native Rust ablation trajectory and
completed native FDTD cutoff tests. Density morphology is recalculated from
the standalone Dimant--Oppenheim equations. All plotted arrays are saved in HDF5.
"""
from pathlib import Path
import hashlib
import json
import subprocess

import h5py
import numpy as np
from scipy.constants import epsilon_0, electron_mass, elementary_charge, atomic_mass

from meteor_rcs.do_density import electron_density

ROOT = Path(__file__).resolve().parent



def source_quantities(loss, speed, beta, length, mass_air):
    """SI source rate, production line density, and DO density normalization."""
    mass_si = 28.085*atomic_mass
    production = beta*loss/mass_si
    q = production/speed
    nstar = q*(1+mass_si/mass_air)/(2*np.sqrt(6*np.pi)*length**2)
    return production, q, nstar


def collision_lengths(speed, temperature, number_density):
    """Fast-projectile atmospheric path and grain-frame thermal-neutral path."""
    from scipy.constants import Boltzmann
    # Bronshten (1983), adopted by Sugar et al. (2018), section 5.3.
    cross_section = 5.61e-19*(np.asarray(speed)/1000)**(-.8)
    rate = number_density*cross_section*speed
    thermal_speed = np.sqrt(Boltzmann*temperature/(28.085*atomic_mass))
    return 1/(number_density*cross_section), thermal_speed/rate


def native_plots():
    """HDF5 is the data product; JSON only transports arrays over stdin."""
    with h5py.File(ROOT/'data.h5') as f:
        fields = {
            'altitude': f['trajectory/altitude_m'][:]/1000,
            'loss': -f['trajectory/dmdt_kg_s'][:],
            'temperature': f['trajectory/temperature_k'][:],
            'speeds': f['ionization/speed_kms'][:], 'beta': f['ionization/beta'][:],
            'z': f['density/z_over_lambda'][:], 'r': f['density/r_over_lambda'][:],
            'density': f['density/ne_over_nstar'][:].ravel(),
            'radius': f['cutoff/radius_m'][:], 'rcs': f['cutoff/rcs_m2'][:],
        }
        fixed_length=f.attrs['density_100km_lambda_m']
    payload = {key: [float(v) if np.isfinite(v) else None for v in values] for key, values in fields.items()}
    with h5py.File(ROOT/'ablation_profiles.h5') as f:
        payload['profiles']=[dict(speed=float(g.attrs['initial_speed_km_s']),
            altitude=g['altitude_km'][:].tolist(),velocity=g['velocity_km_s'][:].tolist(),
            mass=(g['mass_kg'][:]/1e-9).tolist(),loss=(abs(g['mass_loss_rate_kg_s'][:])/1e-9).tolist(),
            temperature=g['temperature_k'][:].tolist()) for g in f.values() if isinstance(g,h5py.Group)]
    payload['density_length_m']=float(fixed_length)
    result=subprocess.run(['cargo', 'run', '--quiet', '--release', '--manifest-path',
        str(ROOT/'plots/Cargo.toml'), '--', str(ROOT/'assets')],
        input=json.dumps(payload, allow_nan=False), text=True, check=False,capture_output=True)
    if result.returncode:
        print(result.stderr)
        result.check_returncode()
    gallery=json.loads(result.stdout)
    for z,r,value in gallery['checks']:
        np.testing.assert_allclose(value,electron_density(z,r),rtol=2e-7)
    with h5py.File(ROOT/'data.h5','a') as f:
        for key,value in gallery.items():f['gallery/'+key]=np.asarray(value,dtype=float)


def main():
    (ROOT/'assets').mkdir(exist_ok=True)
    with h5py.File(ROOT/'inputs.h5') as f:
        t={key:f['trajectory'][key][:] for key in f['trajectory']}
        h=t['altitude_m']/1000
        loss=-t['dmdt_kg_s']; q=t['electron_production_s1']/t['velocity_m_s']
        sample=int(np.argmin(abs(h-102.5)))
        cutoff={key:f['cutoff'][key][:] for key in f['cutoff']}
        n100=np.exp(np.interp(100000.,f['msis_altitude_m'][:],np.log(f['neutral_number_density_m3'][:])))
        ell100,lambda100=collision_lengths(50000.,2000.,n100)
        # Independently reproduce the density normalization from MSIS inputs.
        rho=np.exp(np.interp(t['altitude_m'][sample],f['msis_altitude_m'][:],np.log(f['msis_raw'][:,0])))
        air_log=np.exp(np.interp(t['altitude_m'][sample],f['msis_altitude_m'][:],np.log(f['neutral_number_density_m3'][:])))
        derived=source_quantities(loss[sample],t['velocity_m_s'][sample],t['beta_si_primary'][sample],
            t['mean_free_path_m'][sample],rho/air_log)
        np.testing.assert_allclose(derived,[t['electron_production_s1'][sample],q[sample],t['n_star_m3'][sample]],rtol=1e-7)
    speeds=np.linspace(8,80,300)
    x=18.5e-6*np.maximum(speeds-11,0)**2*speeds**.8
    beta=x/(1+x)
    z=np.linspace(-2,6,121);r=np.linspace(-3,3,81)
    density=np.array([[electron_density(zz,abs(rr)) for zz in z] for rr in r])
    finite=np.isfinite(density)
    assert np.min(density[finite])>-1e-10
    # Keep the widest-box duplicate at each physical radius.
    keep=[np.flatnonzero(cutoff['cutoff_lengths']==k)[-1] for k in np.unique(cutoff['cutoff_lengths'])]
    radius=cutoff['radius_m'][keep];rcs=cutoff['rcs_m2'][keep]
    frequency=53.5e6
    ncrit=epsilon_0*electron_mass*(2*np.pi*frequency)**2/elementary_charge**2
    with h5py.File(ROOT/'data.h5','w') as f:
        f['density/z_over_lambda']=z;f['density/r_over_lambda']=r;f['density/ne_over_nstar']=density
        for key,value in t.items():f['trajectory/'+key]=value
        f['trajectory/q_m1']=q
        f['ionization/speed_kms']=speeds;f['ionization/beta']=beta
        f['cutoff/radius_m']=radius;f['cutoff/rcs_m2']=rcs
        f['example/production_q_nstar']=derived
        f.attrs.update(density_100km_lambda_m=lambda100,density_100km_air_path_m=ell100,
            density_100km_number_density=n100,density_100km_speed_ms=50000.,density_100km_temperature_k=2000.,sample_index=sample,frequency_hz=frequency,critical_density_m3=ncrit,
            sample_altitude_km=h[sample],sample_speed_kms=t['velocity_m_s'][sample]/1000,
            sample_loss_kg_s=loss[sample],sample_beta=t['beta_si_primary'][sample],
            sample_lambda_m=t['mean_free_path_m'][sample],sample_temperature_k=t['temperature_k'][sample],
            density_status='Point-source DO morphology, not a finite-grain calculation',
            rcs_status='Completed native cutoff sensitivity tests, not a converged production estimate',
            input_sha256=hashlib.sha256((ROOT/'inputs.h5').read_bytes()).hexdigest())
        for name in ['prepare_assets.py','do_density.py','plots/src/main.rs','plots/Cargo.toml','plots/src/gallery.rs','plots/src/support/dimant.rs']:
            f['source/'+name]= (ROOT/name).read_text()
            f.attrs[name+'_sha256']=hashlib.sha256((ROOT/name).read_bytes()).hexdigest()
    native_plots()
    print('Prepared assets; example production/q/nstar:',derived,'critical density:',ncrit)


if __name__=='__main__':main()
