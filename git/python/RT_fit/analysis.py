import sys
import prospect.io.read_results as reader
import matplotlib.pyplot as plt
import numpy as np
from astropy.io import fits
from scipy import stats
import argparse
import os

from os.path import expanduser
home = expanduser("~")

sys.path.insert(1, home+'/prospector') # import from home instead of anaconda 

currentPath = os.path.dirname(__file__)

parser = argparse.ArgumentParser()
parser.add_argument("--path")
args = parser.parse_args()

filePath = '{0}/Prospector_files/fit.h5'.format(args.path)

res, obs, model = reader.results_from(filePath)

best = res["bestfit"]

# Maximum posterior probability sample
imax = np.argmax(res['lnprobability'])

#N = 32768 # number of maximum lnprob values to include
N = res['lnprobability'].shape[0] * res['lnprobability'].shape[1] # all values
print('N is', N)
imaxmult = np.argpartition(res['lnprobability'], -N, axis=None)[-N:]

csz = res["chain"].shape 

i, j = np.unravel_index(imax, res['lnprobability'].shape)
theta_max = res['chain'][i, j, :].copy()
flatchain = res["chain"].reshape(csz[0] * csz[1], csz[2])

max_percentile = np.zeros(model.ndim)
for i in range(model.ndim):
	max_percentile[i] = stats.percentileofscore(flatchain[:,i], theta_max[i])
	print('max percentile', max_percentile[i])

sps = reader.get_sps(res)

# generate fake obs to get full resolution spectra
fake_obs = obs.copy()
fake_obs['spectrum'] = None
fake_obs['wavelength'] = None

spec, phot, x = model.predict(theta_max, obs=obs, sps=sps)

full_spec = model.predict(theta_max, obs=fake_obs, sps=sps)[0]

wave_eff = [f.wave_effective for f in res['obs']['filters']]

print('Maximum posterior probability parameters: ')
file = open(args.path+"/Analysis/bestfit_params.txt", "w") 
for i in range(len(res['theta_labels'])):
    print(res['theta_labels'][i], best['parameter'][i])
    best_value = "{:.4e}".format(best['parameter'][i]) # write value in scientific notation
    file.write(str(res['theta_labels'][i])+': '+str(best_value)+'\n')

# Calculate average chi-squared error between observed (SKIRT) and model (bestfit) photometry
chi2 = 0
for i in range(len(phot)):
        chi2 += (phot[i] - res['obs']['maggies'][i])**2
chi2 = chi2 / len(phot)
    
a = model.params["zred"] + 1

rfw = np.load('{0}/full_rf_wavelengths.npy'.format(currentPath)) # generated from sdss_bands_test read.py

mask = ((a * rfw) >= 1e3) & ((a * rfw) <= 1e8)

plt.figure(figsize=(10,8))

wave_correct = np.load('{0}/Prospector_files/wave.npy'.format(args.path)) # units of microns
wave_correct = wave_correct * 1e4 # convert to Angstroms
spec_correct = np.load('{0}/Prospector_files/spec.npy'.format(args.path)) # units of Jy 
spec_correct = spec_correct / 3631 # convert to maggies

mask_correct = (wave_correct >= 1e3) & (wave_correct <= 1e8)

plt.plot(wave_correct[mask_correct], spec_correct[mask_correct], label="Actual Spectrum")
plt.plot(wave_eff, phot, label="Bestfit Photometry", marker = '^', linewidth=0)
plt.plot((a * rfw)[mask], full_spec[mask], label="Bestfit Spectrum")
plt.plot(wave_eff, res['obs']['maggies'], '-o', label='Observed Photometry', linewidth=0)
#plt.plot(obs['wavelength'], obs['spectrum'], label='Observed Spectrum')
plt.xlabel('Wavelength (Angstroms)', fontsize=16)
plt.ylabel('Flux (Maggies)', fontsize=16)

plt.xscale('log')
plt.yscale('log')

plt.legend()
plt.savefig('{0}/Analysis/compare.png'.format(args.path), dpi=300)

np.save('{0}/Analysis/bestfit_wave.npy'.format(args.path),(a * rfw)[mask])
np.save('{0}/Analysis/bestfit_spec.npy'.format(args.path),full_spec[mask])
np.save('{0}/Analysis/bestfit_photometry_wave_eff.npy'.format(args.path),wave_eff)
np.save('{0}/Analysis/bestfit_photometry_flux.npy'.format(args.path),phot)

# save averaged chi-squared photometry error as text file
f = open('{0}/Analysis/bestfit_chi2.txt'.format(args.path),"w+")
f.write(chi2)
f.close()

# Read bestfit_paramms.txt to get value of mass, tage, and tau

textFile = open(args.path+"/Analysis/bestfit_params.txt', 'r')
lines = textFile.readlines()
    for j in range(len(lines)):
        if lines[j].startswith('mass'):
            mass = float(lines[j].split('mass: ')[1])
        elif lines[j].startswith('tage'):
            age = float(lines[j].split('tage: ')[1]) * 1e9 # convert from Gyr to yr
        elif lines[j].startswith('tau'):
            tau = float(lines[j].split('tau: ')[1]) * 1e9 # convert from Gyr to tr 

