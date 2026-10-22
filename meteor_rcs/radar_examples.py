"""Reproducible ideal radar link calculations; scientific citations in HDF5 metadata."""
from pathlib import Path
import h5py
import numpy as np
from scipy.constants import c, Boltzmann, elementary_charge, epsilon_0, electron_mass, physical_constants
ROOT=Path(__file__).resolve().parent
def received_power(power,gain_tx,gain_rx,frequency,rcs,range_m):
    return power*gain_tx*gain_rx*(c/frequency)**2*rcs/((4*np.pi)**3*range_m**4)
def main():
    # Columns: frequency MHz, peak MW, boresight gain dBi, equivalent noise K.
    rows=np.array([[430,1,61,120],[50,4.5,10*np.log10(4*np.pi*75000/(c/50e6)**2),3000],
                   [440.2,2.5,44.5,150],[233,5,43,150]])
    names=['Arecibo (historical)','Jicamarca (full array)','Millstone Hill (zenith)','EISCAT 3D (design)']
    citations=[
      'https://pmc.ncbi.nlm.nih.gov/articles/PMC5023023/',
      'https://www.diva-portal.org/smash/get/diva2:981094/FULLTEXT01.pdf',
      'https://apollo.haystack.mit.edu/isr/status/data/ ; https://www.sgo.fi/Events/RS2012/l/04_Stromme_US_ISRs.pdf',
      'https://doi.org/10.5194/angeo-38-861-2020']
    power_per_area=received_power(rows[:,1]*1e6,10**(rows[:,2]/10),10**(rows[:,2]/10),rows[:,0]*1e6,1,100e3)
    noise=Boltzmann*rows[:,3]*1e6
    sig_min=10*noise/power_per_area # 10 dB, B=1 MHz, no processing gain or losses
    # A weak, unmagnetized isotropic Gaussian density benchmark.
    ne_total=1e10;a=.1;nu=1e7
    omega=2*np.pi*rows[:,0]*1e6;k=omega/c
    re=physical_constants['classical electron radius'][0]
    sig=4*np.pi*re**2*ne_total**2*np.exp(-4*(k*a)**2)*omega**2/(omega**2+nu**2)
    npeak=ne_total/((2*np.pi)**1.5*a**3)
    wp=np.sqrt(npeak*elementary_charge**2/(epsilon_0*electron_mass))
    with h5py.File(ROOT/'radar_examples.h5','w') as f:
        f['names']=np.array(names,dtype=h5py.string_dtype())
        f['parameters']=rows;f['parameter_units']=np.array(['MHz','MW','dBi','K'],dtype=h5py.string_dtype())
        f['citations']=np.array(citations,dtype=h5py.string_dtype())
        f['power_per_rcs_w_m2']=power_per_area;f['noise_w_1mhz']=noise
        f['sigma_min_m2_10db_1mhz']=sig_min;f['sigma_min_m2_10db_10khz']=sig_min/100
        f['gaussian_sigma_m2']=sig;f['gaussian_received_w']=power_per_area*sig
        f['gaussian_snr_db_10khz']=10*np.log10(power_per_area*sig/(noise/100))
        f.attrs.update(range_m=100000.,loss_factor=1.,snr_threshold_linear=10.,
            gaussian_electron_count=ne_total,gaussian_standard_deviation_m=a,
            gaussian_collision_rate_s1=nu,gaussian_peak_density_m3=npeak,
            gaussian_max_wp_over_omega=wp/min(omega),gaussian_model='First Born, linear matched polarization, no B0; not a DO FDTD prediction')
        sg=np.array([1e-6,1e-4,1e-2])
        maarsy=received_power(736e3,10**3.35,10**3.35,53.5e6,sg,100e3)
        f['worked/rcs_m2']=sg;f['worked/power_w']=maarsy
        f['worked/snr_db']=10*np.log10(maarsy/(Boltzmann*1000*1e4))
        f['worked'].attrs.update(frequency_hz=53.5e6,power_w=736e3,gain_dbi=33.5,temperature_k=1000.,bandwidth_hz=1e4,
            citation='https://doi.org/10.1002/2015JD023291',noise_temperature_assumed=True)
    print('Radar parameters / sigma_min dBsm / Gaussian sigma dBsm / SNR 10kHz')
    for name,param,mn,sg,snr in zip(names,rows,sig_min,sig,10*np.log10(power_per_area*sig/(noise/100))):
        print(name,param,10*np.log10(mn),10*np.log10(sg),snr)
if __name__=='__main__':main()
