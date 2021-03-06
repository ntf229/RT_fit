# Main pipeline
# Runs SKIRT on NIHAO galaxy, fits with Prospector, and analyzes the results 
# to run, use:
# python sph.py --name="image_test2" --dust="False" --inc="45" --maxLevel="7" --wavelengths="100" --numPhotons="1e7" --fitType="GSWLC1" --nwalkers="64" 

import argparse
import os
import shutil
from os.path import expanduser
from timeit import default_timer as timer
import subprocess
import datetime

overwrite = False # if set to True, then delete existing fit.h5 file and fit again

home = expanduser("~")

parser = argparse.ArgumentParser()
parser.add_argument("--name") # project name
parser.add_argument("--dust") # include dust; True or False
parser.add_argument("--inc") # inclination angle (SKIRT parameter)
parser.add_argument("--maxLevel") # maxLevel (SKIRT parameter)
parser.add_argument("--wavelengths") # number of wavelength bins (SKIRT parameter)
parser.add_argument("--numPhotons") # number of photon packages (SKIRT parameter)
parser.add_argument("--fitType") # bands/spectra to use in Prospector fit (eg. GSWLC1)
parser.add_argument("--nwalkers") # number of walkers to use in Prospector fit
args = parser.parse_args()

mainPath=home+"/RT_fit/git"
resourcePath=home+"/RT_fit/resources"
projectPath=home+"/RT_fit/projects/"+args.name 
if args.dust == "True":
  SKIRTPath=home+"/RT_fit/resources/SKIRT/maxLevel"+args.maxLevel+"/wavelengths"+args.wavelengths+"/numPhotons"+args.numPhotons+"/inc"+args.inc+"/dust"
else:
  SKIRTPath=home+"/RT_fit/resources/SKIRT/maxLevel"+args.maxLevel+"/wavelengths"+args.wavelengths+"/numPhotons"+args.numPhotons+"/inc"+args.inc+"/nodust"

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
  shutil.copy(resourcePath+"/NIHAO/dust.txt", SKIRTPath)
  shutil.copy(resourcePath+'/NIHAO/radiation.txt', SKIRTPath)

  if args.dust == "True":
    print('Including dust')
    maxDustFraction = "1e-6" # default value
  else:
    os.system('rm '+SKIRTPath+'/dust.txt')
    os.system('touch '+SKIRTPath+'/dust.txt')
    print('Created empty dust.txt file')

  # move ski file to SKIRT directory
  shutil.copy2(mainPath+'/ski_files/sph.ski', SKIRTPath)

  # change values in newly created .ski file to argparse values
  os.system('python '+mainPath+'/python/RT_fit/modify_ski.py --filePath='+SKIRTPath+'/sph.ski --inc='+args.inc+' --maxLevel='+args.maxLevel+' --wavelengths='+args.wavelengths+' --numPhotons='+args.numPhotons)

  # go to SKIRT directory and run, then cd back
  origDir = os.getcwd()
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
  os.system('rm radiation.txt')
  os.system('rm dust.txt')

  os.chdir(origDir)

  shutil.copy2(SKIRTPath+'/spec.npy', projectPath+'/Prospector_files')
  shutil.copy2(SKIRTPath+'/wave.npy', projectPath+'/Prospector_files')

end = timer()
time_SKIRT = end - start
time_SKIRT = str(datetime.timedelta(seconds=time_SKIRT))
print('Time to get SKIRT SED:', time_SKIRT)  

# create filter_list array from --fitType codename (format: sdss_u0,sdss_g0,sdss_r0,sdss_i0,sdss_z0,galex_FUV,galex_NUV)
if args.fitType == 'GSWLC1':
  filter_list = 'sdss_u0,sdss_g0,sdss_r0,sdss_i0,sdss_z0,galex_FUV,galex_NUV'

# handle prospector fit overwriting and dust inclusion (notice all four params_dust.py and params_no_dust.py calls)
if os.path.exists(projectPath+'/Prospector_files/fit.h5'):
  if overwrite:
    os.remove(projectPath+'/Prospector_files/fit.h5')
    print('removed old fit.h5 file, running Prospector fit')

    # run Prospector fit
    if args.dust == "True":
      os.system('python '+mainPath+'/python/RT_fit/params_dust.py --emcee --nwalkers='+args.nwalkers+' --path='+projectPath+' --filters='+filter_list)
    else:
      os.system('python '+mainPath+'/python/RT_fit/params_no_dust.py --emcee --nwalkers='+args.nwalkers+' --path='+projectPath+' --filters='+filter_list)
  
  else:
    print('skipping Prospector fit, using existing fit.h5 file')
else: 

  # run Prospector fit
  if args.dust == "True":
    os.system('python '+mainPath+'/python/RT_fit/params_dust.py --emcee --nwalkers='+args.nwalkers+' --path='+projectPath+' --filters='+filter_list)
  else:
    os.system('python '+mainPath+'/python/RT_fit/params_no_dust.py --emcee --nwalkers='+args.nwalkers+' --path='+projectPath+' --filters='+filter_list)

# run analysis
os.system('python '+mainPath+'/python/RT_fit/analysis.py --path='+projectPath)

# create a text file recording the parser arguments
f = open(projectPath+"/args.txt","w+")
f.write("name: "+args.name+"\n")
f.write("dust: "+args.dust+"\n")
f.write("inc: "+args.inc+"\n")
f.write("maxLevel: "+args.maxLevel+"\n")
f.write("wavelengths: "+args.wavelengths+"\n")
f.write("numPhotons: "+args.numPhotons+"\n")
f.write("fitType: "+args.fitType+"\n")
f.write("nwalkers: "+args.nwalkers+"\n")
f.close()

print('made it to the end')
