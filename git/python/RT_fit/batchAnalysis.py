# create plots of estimated parameters vs. true parameters for a batch of galaxies

import numpy as np
import matplotlib.pyplot as plt
import os

# Photometry type
phot = ['GSWLC1','DustPedia']

# location to save plots
plotPath = '/scratch/ntf229/RT_fit/plots/'

# 16 galaxies selected by hand from the NIHAO Suite                                                             
galaxies = ['g1.12e12','g1.92e12','g2.39e11','g2.79e12','g3.23e11','g3.49e11','g3.59e11','g3.61e11','g5.31e11','g5.36e11','g5.38e11','g5.55e11','g7.08e11','g7.44e11','g8.26e11','g8.28e11']  

trueMasses = np.zeros((len(galaxies),len(phot)))
trueAges = np.zeros((len(galaxies),len(phot)))
estMasses = np.zeros((len(galaxies),len(phot)))
estAges = np.zeros((len(galaxies),len(phot)))
estTaus = np.zeros((len(galaxies),len(phot)))

for i in range(len(galaxies)):

    for k in range(len(phot)):
        textFilePath = '/scratch/ntf229/RT_fit/resources/NIHAO/TextFiles/'+galaxies[i]+'/'
        bestFitPath = '/scratch/ntf229/RT_fit/projects/'+galaxies[i]+'/maxLevel13/wavelengths250/numPhotons3e8/niter2048/inc0/dust/'+phot[k]+'/walkers256/Analysis/'
    
        # calculate true mass of current galaxy from stars.txt
        stars = np.loadtxt(textFilePath+'stars.txt')
        starMasses = stars[:,7] # units of M_sun
        trueMasses[i,k] = np.sum(starMasses)
        starAges = stars[:,9] # units of yr
        trueAges[i,k] = np.amax(starAges) # age of the oldest star
    
        textFile = open(bestFitPath+'bestfit_params.txt', 'r')
        lines = textFile.readlines()
        for j in range(len(lines)):
            if lines[j].startswith('mass'):
                estMasses[i,k] = float(lines[j].split('mass: ')[1])
            elif lines[j].startswith('tage'):
                estAges[i,k] = float(lines[j].split('tage: ')[1]) * 1e9 # convert from Gyr to yr
            elif lines[j].startswith('tau'):
                estTaus[i,k] = float(lines[j].split('tau: ')[1])

minMass = np.amin([np.amin(trueMasses), np.amin(estMasses)])
maxMass = np.amax([np.amax(trueMasses), np.amax(estMasses)])
plt.figure(figsize=(10,8))
plt.plot([minMass,maxMass],[minMass,maxMass],'--',color='k')
plt.plot(trueMasses[:,0], estMasses[:,0], linewidth=0, marker='o',label=phot[0])
plt.plot(trueMasses[:,1], estMasses[:,1], linewidth=0, marker='o',label=phot[1])
plt.xlabel('True Stellar Mass '+r'$(M_{\odot})$',fontsize=16)
plt.ylabel('Estimated Stellar Mass '+r'$(M_{\odot})$',fontsize=16)
#plt.ylabel(r'$Estimated \ Stellar \ Mass \ (M_{\odot})$',fontsize=16)
plt.xscale('log')
plt.yscale('log')
plt.legend()
plt.savefig(plotPath+phot[0]+'_'+phot[1]+'_massCompare.png',dpi=600)

minAge = np.amin([np.amin(trueAges), np.amin(estAges)])
maxAge = np.amax([np.amax(trueAges), np.amax(estAges)])
plt.figure(figsize=(10,8))
plt.plot([minAge,maxAge],[minAge,maxAge],'--',color='k')
plt.plot(trueAges[:,0], estAges[:,0], linewidth=0, marker='o',label=phot[0])
plt.plot(trueAges[:,1], estAges[:,1], linewidth=0, marker='o',label=phot[1])
plt.xlabel('True Ages (Years)',fontsize=16)
plt.ylabel('Estimated Ages (Years)',fontsize=16)
plt.xscale('log')
plt.yscale('log')
plt.legend()
plt.savefig(plotPath+phot[0]+'_'+phot[1]+'_ageCompare.png',dpi=600)


