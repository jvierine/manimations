"""Small frozen-cloud FDTD teaching calculation; Rust evolves all fields and currents.

The source is an archived copy of the established solver with slice output only.
Full provenance stays inside the HDF5 product. No quantitative convergence claim.
"""
from pathlib import Path
import hashlib,json,os,subprocess,shutil
import h5py,numpy as np
from scipy.interpolate import RegularGridInterpolator
from meteor_rcs.do_density import electron_density
ROOT=Path(__file__).resolve().parent
SOLVER=ROOT/'current_solver'
def main():
    SOLVER.mkdir(exist_ok=True);(SOLVER/'src').mkdir(exist_ok=True)
    source=(SOLVER/'src/main.rs').read_text()
    # Bounded, small pilot: 64^3 cells, three threads, no remote calculation.
    n=64;dx=.05;length=.16;support=1.;nstar=1e12;cap=1e14
    temp=Path('/tmp/meteor-current-preview');temp.mkdir(exist_ok=True)
    rr=np.r_[0,np.geomspace(1e-4,7.,100)];zz=np.linspace(-7,7,161)
    field=np.array([[electron_density(z,r) for r in rr] for z in zz])
    field=np.minimum(np.nan_to_num(field,nan=cap/nstar),cap/nstar)
    interp=RegularGridInterpolator((zz,rr),np.log1p(np.maximum(field,0)),bounds_error=False,fill_value=0.)
    density=np.zeros((3,n,n,n),dtype='<f8')
    axes=(np.arange(n)-n/2)*dx
    for component in range(3):
        coord=[axes+(dx/2 if q==component else 0) for q in range(3)]
        x,y,z=np.meshgrid(*coord,indexing='ij');R=np.sqrt(x*x+y*y+z*z)
        # Trajectory is the z axis, side-on to radar propagation along +x.
        points=np.c_[z.ravel()/length,np.hypot(x,y).ravel()/length]
        values=np.minimum(nstar*np.expm1(interp(points)).reshape(R.shape),cap)
        taper=.5*(1+np.cos(np.pi*np.clip((R/support-.8)/.2,0,1)))
        density[component]=values*taper*(R<support)
    density.tofile(temp/'density.bin')
    conf=dict(n=n,dx_m=dx,pml_cells=8,frequency_hz=53.5e6,collision_rate_s1=1e7,
              magnetic_field_t=[-50e-6,0,0],polarization='linear',support_radius_m=support,periods=4,
              density_file=str(temp/'density.bin'),output_file=str(temp/'result.json'),
              threads=3,field_frames=240,field_file=str(temp/'slices.bin'))
    (temp/'config.json').write_text(json.dumps(conf))
    env=dict(os.environ,MPICC='/opt/homebrew/bin/mpicc',CARGO_TARGET_DIR='/tmp/meteor-current-target')
    subprocess.run(['cargo','build','--release','--manifest-path',str(SOLVER/'Cargo.toml')],check=True,env=env)
    subprocess.run(['/tmp/meteor-current-target/release/meteor-fdtd',str(temp/'config.json')],check=True,env=env)
    result=json.loads((temp/'result.json').read_text())
    frames=np.fromfile(temp/'slices.bin',dtype='<f4').reshape(-1,2,n,n)
    dt=result['dt_s'];t=np.array(result['field_times_s'])
    assert np.all(np.isfinite(frames))
    with h5py.File(ROOT/'current_preview.h5','w') as f:
        f['electric_z_v_m']=frames[:,0];f['current_z_a_m2']=frames[:,1]
        f['time_e_s']=t;f['time_j_s']=t-dt/2
        f['axis_x_m']=axes;f['axis_z_m']=axes+dx/2
        f['density_z_edges_m3']=density[2]
        f['source/rust_main']=source;f['source/configuration']=json.dumps(conf)
        f.attrs.update(frequency_hz=conf['frequency_hz'],collision_rate_s1=conf['collision_rate_s1'],
            incident_peak_v_m=1.,lambda_t_m=length,nstar_m3=nstar,cap_m3=cap,
            support_radius_m=support,grid_n=n,dx_m=dx,dt_s=dt,elapsed_s=result['elapsed_s'],
            note='Illustrative finite-grid frozen-cloud solution, not a converged RCS result',
            rust_source_sha256=hashlib.sha256(source.encode()).hexdigest())
    out=ROOT/'webgl'
    data=dict(peakFrame=int(np.argmax(np.max(abs(frames[:,1]),axis=(1,2)))),n=n,axis=axes.tolist(),times=(t*1e9).tolist(),
              j=frames[:,1].transpose(0,2,1).ravel().tolist(),e=frames[:,0].transpose(0,2,1).ravel().tolist(),
              jscale=float(np.max(abs(frames[:,1]))),escale=float(np.max(abs(frames[:,0]))))
    # Runtime transport only; the retained scientific data product is HDF5.
    (out/'current.json').write_text(json.dumps(data,separators=(',',':'),allow_nan=False))
    print('Recorded real field/current slices',frames.shape,'runtime',result['elapsed_s'])
if __name__=='__main__':main()
