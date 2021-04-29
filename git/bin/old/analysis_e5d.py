# Runs the analysis for every 5 degrees inclination angle
# to run, use:
# python analysis_e5d.py --dust="False" --maxLevel="7" --wavelengths="100" --numPhotons="1e7" --pixels="1000" --fitType="GSWLC1" --nwalkers="256"

import argparse
import os
import shutil
from os.path import expanduser
from timeit import default_timer as timer
import subprocess
import datetime

#home = expanduser("~")
home = "/scratch/ntf229"

parser = argparse.ArgumentParser()
parser.add_argument("--dust") # include dust; True or False
parser.add_argument("--maxLevel") # maxLevel (SKIRT parameter)
parser.add_argument("--wavelengths") # number of wavelength bins (SKIRT parameter)
parser.add_argument("--numPhotons") # number of photon packages (SKIRT parameter)
parser.add_argument("--pixels") # number of pixels (square) for image (SKIRT parameter)
parser.add_argument("--fitType") # bands/spectra to use in Prospector fit (eg. GSWLC1)                                                                                         
parser.add_argument("--nwalkers") # number of walkers to use in Prospector fit
args = parser.parse_args()

#mainPath=home+"/RT_fit/git"
mainPath=expanduser("~")+"/RT_fit/git" 
resourcePath=expanduser("~")+"/RT_fit/resources"
if args.dust == "True":
  SKIRTPath=home+"/RT_fit/resources/SKIRT/maxLevel"+args.maxLevel+"/wavelengths"+args.wavelengths+"/numPhotons"+args.numPhotons+"/every5deg/dust"
else:
  SKIRTPath=home+"/RT_fit/resources/SKIRT/maxLevel"+args.maxLevel+"/wavelengths"+args.wavelengths+"/numPhotons"+args.numPhotons+"/every5deg/nodust"

# create new directories for each inclination angle and run analysis.py 
for i in range(0,91,5):
    
  if args.dust == "True":
    inc_path = home+"/RT_fit/resources/SKIRT/maxLevel"+args.maxLevel+"/wavelengths"+args.wavelengths+"/numPhotons"+args.numPhotons+"/inc"+str(i)+"/dust"
    projectPath = home+"/RT_fit/projects/maxLevel"+args.maxLevel+"/wavelengths"+args.wavelengths+"/numPhotons"+args.numPhotons+"/inc"+str(i)+"/dust/"+args.fitType+"/walkers"+args.nwalkers
      
  if args.dust == "False":
    inc_path = home+"/RT_fit/resources/SKIRT/maxLevel"+args.maxLevel+"/wavelengths"+args.wavelengths+"/numPhotons"+args.numPhotons+"/inc"+str(i)+"/nodust"
    projectPath = home+"/RT_fit/projects/maxLevel"+args.maxLevel+"/wavelengths"+args.wavelengths+"/numPhotons"+args.numPhotons+"/inc"+str(i)+"/dust/"+args.fitType+"/walkers"+args.nwalkers
      
  os.system('mkdir -p '+projectPath+'/Analysis')

  # run analysis                                                                                                                                                                
  os.system('python '+mainPath+'/python/RT_fit/analysis.py --path='+projectPath)

  print('Done with inc'+str(i))
         
print('made it to the end')
