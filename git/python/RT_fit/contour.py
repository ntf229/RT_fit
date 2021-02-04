import sys
sys.path.insert(1, '/Users/nicholasfaucher/prospector') # import from home instead of anaconda 
import prospect.io.read_results as reader
import matplotlib.pyplot as plt
import numpy as np
from astropy.io import fits
from scipy import stats
from scipy.interpolate import griddata
from scipy.stats import kde
import argparse
import os

#currentPath = os.path.dirname(__file__)

parser = argparse.ArgumentParser()
parser.add_argument("--filename")
parser.add_argument("--path")
args = parser.parse_args()

filePath = '{0}/Prospector_files/{1}'.format(args.path, args.filename)

res, obs, model = reader.results_from(filePath)

best = res["bestfit"]

# Maximum posterior probability sample
imax = np.argmax(res['lnprobability'])
csz = res["chain"].shape

#print('prob shape', res['lnprobability'].shape)

i, j = np.unravel_index(imax, res['lnprobability'].shape)
theta_max = res['chain'][i, j, :].copy()
flatchain = res["chain"].reshape(csz[0] * csz[1], csz[2])
flatprob = res['lnprobability'].reshape(csz[0] * csz[1])

# flatchain[:,0] is all mass parameters
# mass logzsol dust2 tage tau duste_umin duste_qpah duste_gamma
# after making duste_qpah fixed: mass logzsol dust2 tage tau duste_umin duste_gamma

num_params = len(theta_max)
print('number of parameters:', num_params)
x_params = [0]
#y_params = [1,2,3,4,5,6,7]
y_params = np.linspace(1,num_params-1,num=num_params-1,dtype=int)

for l in range(len(x_params)):
	for m in range(len(y_params)):

		if x_params[l] != y_params[m]:

			plt.figure(figsize=(10,8))

			mask = flatprob >= np.percentile(flatprob,90)
		
			x = flatchain[:,x_params[l]][mask]
			y = flatchain[:,y_params[m]][mask]
			z = flatprob[mask]
		
			nbins = 200
		
			g = kde.gaussian_kde((x,y))
			xi, yi = np.mgrid[x.min():x.max():nbins*1j, y.min():y.max():nbins*1j]
			zi = g(np.vstack([xi.flatten(), yi.flatten()]))
		
			z_samples = g(np.vstack([x.flatten(), y.flatten()]))
		
			# calculate percentiles
			perc5 = np.percentile(z_samples, 5)
			perc32 = np.percentile(z_samples, 32)
		
			plt.contourf(xi, yi, zi.reshape(xi.shape), 
						levels=[perc5,perc32, np.amax(z_samples)], 
						cmap='Blues', alpha=1) 
		
			plt.xlabel(res['theta_labels'][x_params[l]], fontsize=16)
			plt.ylabel(res['theta_labels'][y_params[m]], fontsize=16)
			plt.xscale('log')
		
			#plt.xlim(plt.gca().get_xlim()[0]*0.9,plt.gca().get_xlim()[1]*1.1)
			#plt.ylim(plt.gca().get_ylim()[0]*0.9,plt.gca().get_ylim()[1]*1.1)
			
			x_range = abs(plt.gca().get_xlim()[1] - plt.gca().get_xlim()[0])
			y_range = abs(plt.gca().get_ylim()[1] - plt.gca().get_ylim()[0])

			plt.xlim(plt.gca().get_xlim()[0] - x_range*0.1, plt.gca().get_xlim()[1] + x_range*0.1)
			plt.ylim(plt.gca().get_ylim()[0] - y_range*0.1, plt.gca().get_ylim()[1] + y_range*0.1)


			plt.savefig('{0}/Analysis/'.format(args.path)+res['theta_labels'][x_params[l]]+'_'+res['theta_labels'][y_params[m]]+'_contour.png', dpi=300)

#plt.show()


