import os
import numpy as np
import matplotlib.pyplot as plt

path = "/mount/owl1/ntf229/fit_simulated_SED_projects/"
all_folders = os.listdir(path)
dust = []
nodust = []

for i in range(len(all_folders)):
	if "nodust" in all_folders[i]:
		nodust.append(all_folders[i])
	else:
		dust.append(all_folders[i])

print('dust:', dust)
print('no dust:', nodust)

inc_dust = np.zeros(len(dust))
mass_dust = np.zeros(len(dust))

inc_nodust = np.zeros(len(nodust))
mass_nodust = np.zeros(len(nodust))

for i in range(len(dust)):

	f = open(path+dust[i]+'/Analysis/bestfit_params.txt', "r")
	inc_dust[i] = dust[i].split('inc')[1]
	for x in f:
		if "mass" in x:
			mass_dust[i] = x.split('mass: ')[1]

for i in range(len(nodust)):

	f = open(path+nodust[i]+'/Analysis/bestfit_params.txt', "r")
	inc_nodust[i] = nodust[i].split('inc')[1].split('_nodust')[0]
	for x in f:
		if "mass" in x:
			mass_nodust[i] = x.split('mass: ')[1]
			
print('\nDust:')
for i in range(len(inc_dust)):
	print('Inclination Angle:',inc_dust[i],'Mass Estimate:',mass_dust[i])

print('\nNo Dust:')
for i in range(len(inc_nodust)):
	print('Inclination Angle:',inc_nodust[i],'Mass Estimate:',mass_nodust[i])


plt.scatter(mass_dust,inc_dust)
plt.title('Including Dust')
plt.xlabel('Mass (Solar Masses)')
plt.ylabel('Inclination Angle (Degrees)')
#plt.savefig(path+'dust_inc_mass.png', dpi=300)

plt.figure()
plt.scatter(mass_nodust,inc_nodust)
plt.title('Including Dust')
plt.xlabel('Mass (Solar Masses)')
plt.ylabel('Inclination Angle (Degrees)')
#plt.savefig(path+'nodust_inc_mass.png', dpi=300)

