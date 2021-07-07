# Runs SKIRT on a specific NIHAO galaxy, fits with Prospector, and analyzes the results 
# to run, use:
# python RT_fit.py --dust="True" --inc="0" --maxLevel="7" --wavelengths="100" --numPhotons="1e7" --pixels="1000" --fitType="GSWLC1" --nwalkers="64" --niter="4096" --galaxy="g1.12e12" 

import argparse
import os
import shutil
from os.path import expanduser
from timeit import default_timer as timer
import subprocess
import datetime
import numpy as np
import sys

print('The code has started')

fitBool = True # if set to True, run Prospector fit and analysis 
overwrite = True # if set to True, then delete existing fit.h5 file and fit again

origDir = os.getcwd()

#home = expanduser("~")
home = "/scratch/ntf229"

parser = argparse.ArgumentParser()
parser.add_argument("--dust") # include dust; True or False
parser.add_argument("--inc") # inclination angle (SKIRT parameter)
parser.add_argument("--maxLevel") # maxLevel (SKIRT parameter)
parser.add_argument("--wavelengths") # number of wavelength bins (SKIRT parameter)
parser.add_argument("--numPhotons") # number of photon packages (SKIRT parameter)
parser.add_argument("--pixels") # number of pixels (square) for image (SKIRT parameter)
parser.add_argument("--fitType") # bands/spectra to use in Prospector fit (eg. GSWLC1)
parser.add_argument("--nwalkers") # number of walkers to use in Prospector fit
parser.add_argument("--niter") # number of steps taken by each walker
parser.add_argument("--galaxy") # name of galaxy 
args = parser.parse_args()

#mainPath=home+"/RT_fit/git"
mainPath=expanduser("~")+"/RT_fit/git"
#resourcePath=home+"/RT_fit/resources"
resourcePath=home+"/RT_fit/resources/NIHAO/TextFiles/"+args.galaxy
#projectPath=home+"/RT_fit/projects/"+args.name 
if args.dust == "True":
  SKIRTPath=home+"/RT_fit/resources/SKIRT/"+args.galaxy+"/maxLevel"+args.maxLevel+"/wavelengths"+args.wavelengths+"/numPhotons"+args.numPhotons+"/inc"+args.inc+"/dust"
  projectPath = home+"/RT_fit/projects/"+args.galaxy+"/maxLevel"+args.maxLevel+"/wavelengths"+args.wavelengths+"/numPhotons"+args.numPhotons+"/niter"+args.niter+"/inc"+args.inc+"/dust/"+args.fitType+"/walkers"+args.nwalkers  
else:
  SKIRTPath=home+"/RT_fit/resources/SKIRT/"+args.galaxy+"/maxLevel"+args.maxLevel+"/wavelengths"+args.wavelengths+"/numPhotons"+args.numPhotons+"/inc"+args.inc+"/nodust"
  projectPath = home+"/RT_fit/projects/"+args.galaxy+"/maxLevel"+args.maxLevel+"/wavelengths"+args.wavelengths+"/numPhotons"+args.numPhotons+"/niter"+args.niter+"/inc"+args.inc+"/dust/"+args.fitType+"/walkers"+args.nwalkers
# create filter_list array from --fitType codename (format: sdss_u0,sdss_g0,sdss_r0,sdss_i0,sdss_z0,galex_FUV,galex_NUV)

if args.fitType == 'GSWLC1':
  print('Using GWSLC1')
  filter_list = 'sdss_u0,sdss_g0,sdss_r0,sdss_i0,sdss_z0,galex_FUV,galex_NUV'
elif args.fitType == 'DustPedia':
  print('Using DustPedia')
  filter_list = 'sdss_u0,sdss_g0,sdss_r0,sdss_i0,sdss_z0,galex_FUV,galex_NUV,'\
                 'twomass_J,twomass_H,twomass_Ks,wise_w1,wise_w2,wise_w3,wise_w4,'\
                 'spitzer_irac_ch1,spitzer_irac_ch2,spitzer_irac_ch3,spitzer_irac_ch4,'\
                 'spitzer_mips_24,spitzer_mips_70,spitzer_mips_160,herschel_pacs_70,'\
                 'herschel_pacs_100,herschel_pacs_160,herschel_spire_ext_250,'\
                 'herschel_spire_ext_350,herschel_spire_ext_500'
  
# make directories if they don't already exist
os.system('mkdir -p '+projectPath+'/Prospector_files')
os.system('mkdir -p '+projectPath+'/Analysis')

start = timer()

if os.path.isfile(SKIRTPath+'/spec.npy'):
  print('SKIRT generated SED already exists')
  shutil.copy(SKIRTPath+'/spec.npy', projectPath+'/Prospector_files')
  shutil.copy(SKIRTPath+'/wave.npy', projectPath+'/Prospector_files')

else:
  print('Generating SKIRT SED')
  os.system('mkdir -p '+SKIRTPath)
  # copy dust and radiation text files to SKIRT directory
  shutil.copy(resourcePath+'/gas.txt', SKIRTPath+'/gas.txt')
  shutil.copy(resourcePath+'/stars.txt', SKIRTPath+'/stars.txt')

  if args.dust == "True":
    print('Including dust')
  else:
    os.system('rm '+SKIRTPath+'/gas.txt')
    os.system('touch '+SKIRTPath+'/gas.txt')
    print('Created empty dust.txt file')

  # move ski file to SKIRT directory
  shutil.copy2(mainPath+'/ski_files/template.ski', SKIRTPath+'/sph.ski')

  # calculate size of galaxy image from text files
  gas = np.loadtxt(SKIRTPath+'/gas.txt')
  stars = np.loadtxt(SKIRTPath+'/stars.txt')

  xLengthGas = (np.amax(gas[:,0]) - np.amin(gas[:,0]))/2
  yLengthGas = (np.amax(gas[:,1]) - np.amin(gas[:,1]))/2
  zLengthGas = (np.amax(gas[:,2]) - np.amin(gas[:,2]))/2

  xLengthStars = (np.amax(stars[:,0]) - np.amin(stars[:,0]))/2
  yLengthStars = (np.amax(stars[:,1]) - np.amin(stars[:,1]))/2
  zLengthStars = (np.amax(stars[:,2]) - np.amin(stars[:,2]))/2

  maxLength = np.amax([xLengthGas, yLengthGas, zLengthGas, xLengthStars, yLengthStars, zLengthStars])

  print('maxLength:', maxLength)

  # change values in newly created .ski file to argparse values
  os.system('python '+mainPath+'/python/RT_fit/modify_template_ski.py --filePath='+SKIRTPath+'/sph.ski --inc='+args.inc+' --maxLevel='+args.maxLevel+' --wavelengths='+args.wavelengths+' --numPhotons='+args.numPhotons+' --pixels='+args.pixels+' --size='+str(maxLength/3))

  # go to SKIRT directory and run, then cd back
  os.chdir(SKIRTPath)
  os.system('skirt sph.ski')
  os.system('python -m pts.do plot_seds .')
  os.system('python -m pts.do make_images .')

  # delete all files except SED and .ski files
  #files_in_directory = os.listdir(SKIRTPath)
  #filtered_files = [file for file in files_in_directory if (file.endswith(".txt") or file.endswith(".pdf") or file.endswith(".fits") or file.endswith(".dat") or file.endswith(".xml") )]
  #for file in filtered_files:
  #  path_to_file = os.path.join(SKIRTPath, file)
  #  os.remove(path_to_file)

  # just delete radiation and dust text files
  os.system('rm stars.txt')
  os.system('rm gas.txt')

if fitBool:
  print('starting fit')
else:
  print('skipping fit')
  sys.exit()
  
os.chdir(origDir)

shutil.copy2(SKIRTPath+'/spec.npy', projectPath+'/Prospector_files')
shutil.copy2(SKIRTPath+'/wave.npy', projectPath+'/Prospector_files')

end = timer()
time_SKIRT = end - start
time_SKIRT = str(datetime.timedelta(seconds=time_SKIRT))
print('Time to get SKIRT SED:', time_SKIRT)  

# handle prospector fit overwriting and dust inclusion (notice all four params_dust.py and params_no_dust.py calls)
if os.path.exists(projectPath+'/Prospector_files/fit.h5'):
  if overwrite:
    os.remove(projectPath+'/Prospector_files/fit.h5')
    print('removed old fit.h5 file, running Prospector fit')

    # run Prospector fit
    if args.dust == "True":
      os.system('python '+mainPath+'/python/RT_fit/params_dust.py --emcee --nwalkers='+args.nwalkers+' --path='+projectPath+' --filters='+filter_list+' --niter='+args.niter)
    else:
      os.system('python '+mainPath+'/python/RT_fit/params_no_dust.py --emcee --nwalkers='+args.nwalkers+' --path='+projectPath+' --filters='+filter_list+' --niter='+args.niter)
  
  else:
    print('skipping Prospector fit, using existing fit.h5 file')
else: 

  # run Prospector fit
  if args.dust == "True":
    os.system('python '+mainPath+'/python/RT_fit/params_dust.py --emcee --nwalkers='+args.nwalkers+' --path='+projectPath+' --filters='+filter_list+' --niter='+args.niter)
  else:
    os.system('python '+mainPath+'/python/RT_fit/params_no_dust.py --emcee --nwalkers='+args.nwalkers+' --path='+projectPath+' --filters='+filter_list+' --niter='+args.niter)

# run analysis
os.system('python '+mainPath+'/python/RT_fit/analysis.py --path='+projectPath)

# create a text file recording the parser arguments
f = open(projectPath+"/args.txt","w+")
f.write("dust: "+args.dust+"\n")
f.write("inc: "+args.inc+"\n")
f.write("maxLevel: "+args.maxLevel+"\n")
f.write("wavelengths: "+args.wavelengths+"\n")
f.write("numPhotons: "+args.numPhotons+"\n")
f.write("fitType: "+args.fitType+"\n")
f.write("nwalkers: "+args.nwalkers+"\n")
f.write("niter: "+args.niter+"\n")
f.write("galaxy: "+args.galaxy+"\n")
f.close()

print('made it to the end of inc'+args.inc)

