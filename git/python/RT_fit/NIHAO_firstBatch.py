# NIHAO Processing
# Takes NIHAO data files and turns them into SKIRT text files
# Also calculate azimuth and inclination angles corresponding to face-on

# Steps:
# 1. Find center of mass (stars/cold gas)
# 2. Take successive shells between two radii centered around the center of mass. 
#    At each step, calculate the average density inside the shell, and the average density in the shell.
#    Once the ratio (density_shell/density_inside) is less than ~0.2, multiply this radius by some number (maybe 1.5 or 2) 
#    and use this distance for the x,y,z cuts. The benefit of doing this is that it is a local calculation; 
#    it won’t “see” any satellites orbiting in the distance. 
# 3. Make stars and gas text files for SKIRT
# 4. Calculate net angular momentum vector around center of mass (stars/cold gas)
# 5. Calculate azimuth and inclination angles that correspond to looking down the net angular momentum vector (face-on)
# 6. Save record of angular momentum vector, face-on azimuth and inclination angles 

import os
import numpy as np
import matplotlib.pyplot as plt
import pynbody

interval = 1 # can be used to skip particles

# 16 galaxies selected by hand from the NIHAO Suite
galaxies = ['g1.12e12','g1.92e12','g2.39e11','g2.79e12','g3.23e11','g3.49e11','g3.59e11','g3.61e11','g5.31e11','g5.36e11','g5.38e11','g5.55e11','g7.08e11','g7.44e11','g8.26e11','g8.28e11']

# two galaxies for testing
#galaxies = ["g1.12e12","g1.92e12"]
#galaxies = ["g1.92e12"]

for i in range(len(galaxies)):
    
    filePath = "/scratch/ntf229/FirstBatch/"+galaxies[i]+"/"+galaxies[i]+".01024"
    #os.system('cd /archive/ntf229/FirstBatch/"+galaxies[i]+"/')
    #filePath = galaxies[i]+".01024"
    # Load NIHAO data for current galaxies
    data = pynbody.load(filePath)
    
    full_x_pos = np.float32(data.star['pos'].in_units('pc')[0:-1:interval][:,0])
    full_y_pos = np.float32(data.star['pos'].in_units('pc')[0:-1:interval][:,1])
    full_z_pos = np.float32(data.star['pos'].in_units('pc')[0:-1:interval][:,2])
    full_mass = np.float32(data.star['massform'].in_units('Msol')[0:-1:interval]) 	# in solar masses	
    full_metals = np.float32(data.star['metals'][0:-1:interval])
    full_age = np.float32(data.star['age'].in_units('yr')[0:-1:interval])
    full_x_vel = np.float32(data.star['vel'].in_units('km s**-1')[0:-1:interval][:,0])
    full_y_vel = np.float32(data.star['vel'].in_units('km s**-1')[0:-1:interval][:,1])
    full_z_vel = np.float32(data.star['vel'].in_units('km s**-1')[0:-1:interval][:,2])
    full_smooth = np.float32(data.star['smooth'].in_units('pc')[0:-1:interval])

    full_x_pos_gas = np.float32(data.gas['pos'].in_units('pc')[0:-1:interval][:,0])
    full_y_pos_gas = np.float32(data.gas['pos'].in_units('pc')[0:-1:interval][:,1])
    full_z_pos_gas = np.float32(data.gas['pos'].in_units('pc')[0:-1:interval][:,2])
    full_smooth_gas = np.float32(data.gas['smooth'].in_units('pc')[0:-1:interval])
    full_mass_gas = np.float32(data.gas['mass'].in_units('Msol')[0:-1:interval]) 	# in solar masses	
    full_metals_gas = np.float32(data.gas['metals'][0:-1:interval])
    full_temp_gas = np.float32(data.gas['temp'][0:-1:interval])
    full_x_vel_gas = np.float32(data.gas['vel'].in_units('km s**-1')[0:-1:interval][:,0])
    full_y_vel_gas = np.float32(data.gas['vel'].in_units('km s**-1')[0:-1:interval][:,1])
    full_z_vel_gas = np.float32(data.gas['vel'].in_units('km s**-1')[0:-1:interval][:,2])

    print('Units of temperature:',data.gas['temp'].units)
    
    full_length_star = len(full_x_pos) 	    # starting length
    starIndex = [] 	
    print(full_length_star, 'full star')	# indices to be deleted from data
		
    full_length_gas = len(full_x_pos_gas)     # starting length
    gasIndex = [] 		
    print(full_length_gas, 'full gas')   	# indices to be deleted from data
		
    # Create arrays for cold gas
    
    num_cold = 0 # number of cold gas particles
    cold_ind = [] # indices of gas particles corresponding to cold gas
    for j in range(len(full_mass_gas)):
        if full_temp_gas[j] > 11000:
            cold_ind.append(j) # indices to delete from gas 
            num_cold += 1

    full_x_pos_cold_gas = np.float32(np.delete(full_x_pos_gas,cold_ind))
    full_y_pos_cold_gas = np.float32(np.delete(full_y_pos_gas,cold_ind))
    full_z_pos_cold_gas = np.float32(np.delete(full_z_pos_gas,cold_ind))
    full_smooth_cold_gas = np.float32(np.delete(full_smooth_gas,cold_ind))
    full_mass_cold_gas = np.float32(np.delete(full_mass_gas,cold_ind))
    full_metals_cold_gas = np.float32(np.delete(full_metals_gas,cold_ind))
    full_temp_cold_gas = np.float32(np.delete(full_temp_gas,cold_ind))
    full_x_vel_cold_gas = np.float32(np.delete(full_x_vel_gas,cold_ind))
    full_y_vel_cold_gas = np.float32(np.delete(full_y_vel_gas,cold_ind))
    full_z_vel_cold_gas = np.float32(np.delete(full_z_vel_gas,cold_ind))
    
    print('Number of cold gas particles:', num_cold)

    # Calculate center of mass in stars and cold gas
    x_com = 0
    y_com = 0
    z_com = 0
    total_mass_stars = sum(full_mass)
    #total_mass_gas = sum(full_mass_gas)
    total_mass_cold_gas = sum(full_mass_cold_gas)
    
    # Loop through all stars particles
    for j in range(len(full_mass)):
        x_com += (full_mass[j] * full_x_pos[j])
        y_com += (full_mass[j] * full_y_pos[j])
        z_com += (full_mass[j] * full_z_pos[j])

    # Loop through all cold gas particles
    for j in range(len(full_mass_cold_gas)):
        x_com += (full_mass_cold_gas[j] * full_x_pos_cold_gas[j])
        y_com += (full_mass_cold_gas[j] * full_y_pos_cold_gas[j])
        z_com += (full_mass_cold_gas[j] * full_z_pos_cold_gas[j])

    x_com = x_com / (total_mass_stars + total_mass_cold_gas)
    y_com = y_com / (total_mass_stars + total_mass_cold_gas)
    z_com = z_com / (total_mass_stars + total_mass_cold_gas)

    print(galaxies[i])

    print('x range stars:', np.amin(full_x_pos), np.amax(full_x_pos))
    print('y range stars:', np.amin(full_y_pos), np.amax(full_y_pos))
    print('z range stars:', np.amin(full_z_pos), np.amax(full_z_pos))

    print('x range cold gas:', np.amin(full_x_pos_cold_gas), np.amax(full_x_pos_cold_gas))
    print('y range cold gas:', np.amin(full_y_pos_cold_gas), np.amax(full_y_pos_cold_gas))
    print('z range cold gas:', np.amin(full_z_pos_cold_gas), np.amax(full_z_pos_cold_gas))

    print('x com:', x_com)
    print('y com:', y_com)
    print('z com:', z_com)

    # make new array of radius from com for each particle 
    star_radius = np.sqrt( (full_x_pos - x_com)**2 + (full_y_pos - y_com)**2 + (full_z_pos - z_com)**2 )
    gas_radius = np.sqrt( (full_x_pos_cold_gas - x_com)**2 + (full_y_pos_cold_gas - y_com)**2 + (full_z_pos_cold_gas - z_com)**2 )

    # function to check densities 
    def density(r1, r2, star_mass, gas_mass, star_radius, gas_radius):
        volume_interior = 4/3 * np.pi * r1**3
        volume_shell = (4/3 * np.pi * r2**3) - volume_interior 
        mass_interior = 0
        mass_shell = 0
        
        for j in range(len(star_mass)):
            if star_radius[j] < r1:
                mass_interior += star_mass[j] 
            elif (star_radius[j] >= r1) and (star_radius[j] < r2):
                mass_shell += star_mass[j]
        for j in range(len(gas_mass)):
            if gas_radius[j] < r1:
                mass_interior += gas_mass[j]
            elif (gas_radius[j] >= r1) and (gas_radius[j] < r2):
                mass_shell += gas_mass[j]
                
        density_interior = mass_interior / volume_interior
        density_shell = mass_shell / volume_shell

        return density_interior, density_shell

    num_radii = 250 # number of radii to compute densities at
    radius_buffer = 25 # number of radius shells to skip at the beginning
    max_radius_stars = np.amax(star_radius)
    max_radius_gas = np.amax(gas_radius)
    max_radius = np.amax([max_radius_stars,max_radius_gas])
    print('Maximum radius from com:', max_radius)
    print('Density ratios (shell/interior):')
    for j in range(num_radii-radius_buffer):
        r1 = max_radius / (num_radii - j - radius_buffer + 1) 
        r2 = max_radius / (num_radii - j - radius_buffer)
        density_interior, density_shell = density(r1, r2, full_mass, full_mass_cold_gas, star_radius, gas_radius)
        print('Loop', j, density_shell / density_interior)
        if (density_shell / density_interior) < 0.2:
            print('ratio is less than 0.2')
            break

    # skipping angular momentum for now
    continue 
    print('calculating angular momentum')


    # Calculate net angular momentum components around center of mass
    # L = r x p
    # L_x = (r_y * p_z) - (r_z * p_y)
    # L_y = (r_z * p_x) - (r_x * p_z)
    # L_z = (r_x * p_y) - (r_y * p_x)

    L_x = 0
    L_y = 0
    L_z = 0
    
    # Loop through all star particles                                                                                 
    for j in range(len(full_mass)):

        r_x = full_x_pos[j] - x_com
        r_y = full_y_pos[j] - y_com
        r_z = full_z_pos[j] - z_com

        p_x = full_x_vel[j] * full_mass[j]
        p_y = full_y_vel[j] * full_mass[j]
        p_z = full_z_vel[j] * full_mass[j]
        
        L_x += (r_y * p_z) - (r_z * p_y)
        L_y += (r_z * p_x) - (r_x * p_z)
        L_z += (r_x * p_y) - (r_y * p_x)

    # T_avg is the mass-averaged temperature of gas within radius r
    #T_avg = 

    #plt.figure()
    #plt.hist(full_temp_gas,bins=1000,range=[0, 3e4])
    #plt.xlabel('Temperature (K)')
    #plt.savefig('/home/ntf229/RT_fit/tempDist'+galaxies[i]+'.png', dpi=300)
    
    # Loop through all gas particles
    for j in range(len(full_mass_gas)):

        r_x = full_x_pos_gas[j] - x_com
        r_y = full_y_pos_gas[j] - y_com
        r_z = full_z_pos_gas[j] - z_com

        p_x = full_x_vel_gas[j] * full_mass_gas[j]
        p_y = full_y_vel_gas[j] * full_mass_gas[j]
        p_z = full_z_vel_gas[j] * full_mass_gas[j]

        L_x += (r_y * p_z) - (r_z * p_y)
        L_y += (r_z * p_x) - (r_x * p_z)
        L_z += (r_x * p_y) - (r_y * p_x)

        
    print(galaxies[i])
    print('x_com:', x_com)
    print('y_com:', y_com)
    print('z_com:', z_com)
    print('L_x:', L_x)
    print('L_y:', L_y)
    print('L_z:', L_z)
    
        
