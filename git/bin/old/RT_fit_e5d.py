# Runs the radiative transfer (SKIRT) part of the pipeline and stores it in resources
# to run, use:
# python RT_fit_e5d.py --dust="True" --maxLevel="11" --wavelengths="250" --numPhotons="1e8" --pixels="2000" --fitType="GSWLC1" --nwalkers="256"

import argparse
import os
import shutil
from os.path import expanduser
from timeit import default_timer as timer
import subprocess
import datetime

print('The code has started')

overwrite = False # if set to True, then delete existing fit.h5 file and fit again

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

# check if all the required SKIRT inclination angles have spectra  
SKIRTexists = 0

for i in range(0,91,5):
  if args.dust == "True":
    checkPath = home+"/RT_fit/resources/SKIRT/maxLevel"+args.maxLevel+"/wavelengths"+args.wavelengths+"/numPhotons"+args.numPhotons+"/inc"+str(i)+"/dust"
  else:
    checkPath = home+"/RT_fit/resources/SKIRT/maxLevel"+args.maxLevel+"/wavelengths"+args.wavelengths+"/numPhotons"+args.numPhotons+"/inc"+str(i)+"/nodust"
  if os.path.isfile(checkPath+'/spec.npy'):
    print('SKIRT generated SED already exists for inc'+str(i))
  else:
    SKIRTexists = 1 # one or more SKIRT spectra don't exist, need to run SKIRT
    print('SKIRT spectrum does not exist for inc'+str(i))

if SKIRTexists == 1:
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
  shutil.copy2(mainPath+'/ski_files/sph_e5d.ski', SKIRTPath+'/sph.ski')

  # change values in newly created .ski file to argparse values
  os.system('python '+mainPath+'/python/RT_fit/modify_ski_e5d.py --filePath='+SKIRTPath+'/sph.ski --maxLevel='+args.maxLevel+' --wavelengths='+args.wavelengths+' --numPhotons='+args.numPhotons+' --pixels='+args.pixels)

  # go to SKIRT directory and run, then cd back
  origDir = os.getcwd()
  os.chdir(SKIRTPath)
  os.system('skirt sph.ski')
  os.system('rm radiation.txt')
  os.system('rm dust.txt')

  
# create new directories for each inclination angle and move files there
for i in range(45,91,5):
    
  if args.dust == "True":
    inc_path = home+"/RT_fit/resources/SKIRT/maxLevel"+args.maxLevel+"/wavelengths"+args.wavelengths+"/numPhotons"+args.numPhotons+"/inc"+str(i)+"/dust"
    projectPath = home+"/RT_fit/projects/maxLevel"+args.maxLevel+"/wavelengths"+args.wavelengths+"/numPhotons"+args.numPhotons+"/inc"+str(i)+"/dust/"+args.fitType+"/walkers"+args.nwalkers
      
  if args.dust == "False":
    inc_path = home+"/RT_fit/resources/SKIRT/maxLevel"+args.maxLevel+"/wavelengths"+args.wavelengths+"/numPhotons"+args.numPhotons+"/inc"+str(i)+"/nodust"
    projectPath = home+"/RT_fit/projects/maxLevel"+args.maxLevel+"/wavelengths"+args.wavelengths+"/numPhotons"+args.numPhotons+"/inc"+str(i)+"/dust/"+args.fitType+"/walkers"+args.nwalkers

  if SKIRTexists == 1:  
    os.system('mkdir -p '+inc_path)
    os.system('cp sph_log.txt '+inc_path)
    os.system('cp sph_parameters.xml '+inc_path)
    os.system('mv sph_inc'+str(i)+'_sed.dat '+inc_path)
    os.system('mv sph_inc'+str(i)+'_total.fits '+inc_path)
    os.chdir(inc_path)
    os.system('python -m pts.do plot_seds .')
    os.system('python -m pts.do make_images .')

  os.system('mkdir -p '+projectPath+'/Prospector_files')
  os.system('mkdir -p '+projectPath+'/Analysis')
  #os.system('cp sph_log.txt '+inc_path)
  #os.system('cp sph_parameters.xml '+inc_path)
  #os.system('mv sph_inc'+str(i)+'_sed.dat '+inc_path)
  #os.system('mv sph_inc'+str(i)+'_total.fits '+inc_path)
  #os.chdir(inc_path)
  #os.system('python -m pts.do plot_seds .')
  #os.system('python -m pts.do make_images .')
  #os.chdir(SKIRTPath)

  shutil.copy2(inc_path+'/spec.npy', projectPath+'/Prospector_files')
  shutil.copy2(inc_path+'/wave.npy', projectPath+'/Prospector_files')

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
  #f.write("name: "+args.name+"\n")
  f.write("dust: "+args.dust+"\n")
  f.write("inc: "+str(i)+"\n")
  f.write("maxLevel: "+args.maxLevel+"\n")
  f.write("wavelengths: "+args.wavelengths+"\n")
  f.write("numPhotons: "+args.numPhotons+"\n")
  f.write("fitType: "+args.fitType+"\n")
  f.write("nwalkers: "+args.nwalkers+"\n")
  f.close()

  print('Done with inc'+str(i))
      
os.chdir(origDir)

# remove old directory ("every2degrees")
#os.system('rm -r '+SKIRTPath)
      
print('made it to the end')
