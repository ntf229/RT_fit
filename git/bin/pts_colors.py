
import os
import shutil
import subprocess
import datetime


path = '/home/ntf229/RT_fit/resources/SKIRT/maxLevel11/wavelengths30/numPhotons3e7/every2deg/dust/'

os.chdir(path)
os.system('python -m pts.do make_images . --name GALEXFUV_SDSSR_IRAS100 --colors GALEX_GALEX_FUV,SLOAN_SDSS_R,IRAS_IRAS_100')

print('made it to the end')

