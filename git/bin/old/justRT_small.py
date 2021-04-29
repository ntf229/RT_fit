# Runs the radiative transfer (SKIRT) part of the pipeline and stores it in resources
# to run, use:
# python justRT.py --dust="False" --inc="90" --maxLevel="7" --wavelengths="100" --numPhotons="1e7" 

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
parser.add_argument("--dust") # include dust; True or False
parser.add_argument("--inc") # inclination angle (SKIRT parameter)
parser.add_argument("--maxLevel") # maxLevel (SKIRT parameter)
parser.add_argument("--wavelengths") # number of wavelength bins (SKIRT parameter)
parser.add_argument("--numPhotons") # number of photon packages (SKIRT parameter)
args = parser.parse_args()

mainPath=home+"/RT_fit/git"
resourcePath=home+"/RT_fit/resources"
if args.dust == "True":
  SKIRTPath=home+"/RT_fit/resources/SKIRT/maxLevel"+args.maxLevel+"/wavelengths"+args.wavelengths+"/numPhotons"+args.numPhotons+"/inc"+args.inc+"/dust"
else:
  SKIRTPath=home+"/RT_fit/resources/SKIRT/maxLevel"+args.maxLevel+"/wavelengths"+args.wavelengths+"/numPhotons"+args.numPhotons+"/inc"+args.inc+"/nodust"

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

end = timer()
time_SKIRT = end - start
time_SKIRT = str(datetime.timedelta(seconds=time_SKIRT))
print('Time to get SKIRT SED:', time_SKIRT)  

print('made it to the end')
