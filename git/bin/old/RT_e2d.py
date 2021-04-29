# Runs the radiative transfer (SKIRT) part of the pipeline and stores it in resources
# to run, use:
# python justRT.py --dust="False" --maxLevel="7" --wavelengths="100" --numPhotons="1e7" --pixels="1000"

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
parser.add_argument("--maxLevel") # maxLevel (SKIRT parameter)
parser.add_argument("--wavelengths") # number of wavelength bins (SKIRT parameter)
parser.add_argument("--numPhotons") # number of photon packages (SKIRT parameter)
parser.add_argument("--pixels") # number of pixels (square) for image (SKIRT parameter)
args = parser.parse_args()

mainPath=home+"/RT_fit/git"
resourcePath=home+"/RT_fit/resources"
if args.dust == "True":
  SKIRTPath=home+"/RT_fit/resources/SKIRT/maxLevel"+args.maxLevel+"/wavelengths"+args.wavelengths+"/numPhotons"+args.numPhotons+"/every2deg/dust"
else:
  SKIRTPath=home+"/RT_fit/resources/SKIRT/maxLevel"+args.maxLevel+"/wavelengths"+args.wavelengths+"/numPhotons"+args.numPhotons+"/every2deg/nodust"

start = timer()

if os.path.isfile(SKIRTPath+'/spec.npy'):
  print('SKIRT generated SED already exists')
  shutil.copy(SKIRTPath+'/spec.npy', projectPath+'/Prospector_files')
  shutil.copy(SKIRTPath+'/wave.npy', projectPath+'/Prospector_files')

else:
  print('Generating SKIRT SED')
  os.system('mkdir -p '+SKIRTPath)
  # copy dust and radiation text files to SKIRT directory
  shutil.copy(resourcePath+"/NIHAO/gas_bigger.txt", SKIRTPath+'/dust.txt')
  shutil.copy(resourcePath+'/NIHAO/stars_bigger.txt', SKIRTPath+'/radiation.txt')

  if args.dust == "True":
    print('Including dust')
  else:
    os.system('rm '+SKIRTPath+'/dust.txt')
    os.system('touch '+SKIRTPath+'/dust.txt')
    print('Created empty dust.txt file')

  # move ski file to SKIRT directory
  shutil.copy2(mainPath+'/ski_files/sph_e2d.ski', SKIRTPath+'/sph.ski')

  # change values in newly created .ski file to argparse values
  os.system('python '+mainPath+'/python/RT_fit/modify_ski_e2d.py --filePath='+SKIRTPath+'/sph.ski --maxLevel='+args.maxLevel+' --wavelengths='+args.wavelengths+' --numPhotons='+args.numPhotons+' --pixels='+args.pixels)

  # go to SKIRT directory and run, then cd back
  origDir = os.getcwd()
  os.chdir(SKIRTPath)
  os.system('skirt sph.ski')
  os.system('rm radiation.txt')
  os.system('rm dust.txt')

  # create new directories for each inclination angle and move files there
  for i in range(0,91,2):
    if args.dust == "True":
      inc_path = home+"/RT_fit/resources/SKIRT/maxLevel"+args.maxLevel+"/wavelengths"+args.wavelengths+"/numPhotons"+args.numPhotons+"/inc"+str(i)+"/dust"
      os.system('mkdir -p '+inc_path)
      os.system('cp sph_log.txt '+inc_path)
      os.system('cp sph_parameters.xml '+inc_path)
      os.system('mv sph_inc'+str(i)+'_sed.dat '+inc_path)
      os.system('mv sph_inc'+str(i)+'_total.fits '+inc_path)
      os.chdir(inc_path)
      os.system('python -m pts.do plot_seds .')
      os.system('python -m pts.do make_images .')
      os.chdir(SKIRTPath)    

    if args.dust == "False":
      inc_path = home+"/RT_fit/resources/SKIRT/maxLevel"+args.maxLevel+"/wavelengths"+args.wavelengths+"/numPhotons"+args.numPhotons+"/inc"+str(i)+"/nodust"
      os.system('mkdir -p '+inc_path)
      os.system('cp sph_log.txt '+inc_path)
      os.system('cp sph_parameters.xml '+inc_path)
      os.system('mv sph_inc'+str(i)+'_sed.dat '+inc_path)
      os.system('mv sph_inc'+str(i)+'_total.fits '+inc_path)
      os.chdir(inc_path)
      os.system('python -m pts.do plot_seds .')
      os.system('python -m pts.do make_images .')
      os.chdir(SKIRTPath)

os.chdir(origDir)

# remove old directory ("every2degrees")
os.system('rm -r '+SKIRTPath)
      
end = timer()
time_SKIRT = end - start
time_SKIRT = str(datetime.timedelta(seconds=time_SKIRT))
print('Time to get SKIRT SED:', time_SKIRT)  

print('made it to the end')
