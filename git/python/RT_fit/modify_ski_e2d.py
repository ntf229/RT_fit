# creates the ski file that uses many instruments for varying inclination angles
# changes .ski file
# begin line with 'SKIRT/' for skirt parameters
# use a unique parent header after the '/' to point to each parameter
# example: SKIRT/GeometricSource/scaleLength "2000 pc"

import xml.etree.ElementTree as ET
import argparse

parser = argparse.ArgumentParser()
parser.add_argument("--filePath") # path to .ski file
parser.add_argument("--maxLevel") # maxLevel (SKIRT parameter)
parser.add_argument("--wavelengths") # number of wavelength bins (SKIRT parameter)
parser.add_argument("--numPhotons") # number of photon packages (SKIRT parameter)
parser.add_argument("--pixels") # number of pixels (square) for image (SKIRT parameter)
args = parser.parse_args()

tree = ET.parse(args.filePath)
root = tree.getroot()

# MonteCarloSimulation/numPackets 1e7
# FullInstrument/inclination 0_deg
# radiationFieldWLG/LogWavelengthGrid/numWavelengths
# dustEmissionWLG/LogWavelengthGrid/numWavelengths
# defaultWavelengthGrid/LogWavelengthGrid/numWavelengths

d = {
    'FullInstrument/numPixelsX' : str(args.pixels),
    'FullInstrument/numPixelsY' : str(args.pixels),
	'DensityTreePolicy/maxLevel' : str(args.maxLevel),
	'MonteCarloSimulation/numPackets' : str(args.numPhotons),
	'radiationFieldWLG/LogWavelengthGrid/numWavelengths' : str(args.wavelengths),
	'dustEmissionWLG/LogWavelengthGrid/numWavelengths' : str(args.wavelengths),
	'defaultWavelengthGrid/LogWavelengthGrid/numWavelengths' : str(args.wavelengths)
}


# store config.txt inputs as dictionary 
#d = {}
#with open(args.projectPath+"/config.txt") as f:
#	for line in f:
#		(key, val) = line.split()
#		d[key] = val
#print(d)


for name, value in d.items():
	s = name.split('/')
	print('split:', s)
	print('length:', len(s))
	print(s[-1], value)

	for item in root.iter(s[0]):
		if len(s) == 2:
			item.set(s[-1], value.replace("_", " "))
		if len(s) == 3:
			for sub_item in item:
				sub_item.set(s[-1], value.replace("_", " "))

tree.write(args.filePath, encoding='UTF-8', xml_declaration=True)

