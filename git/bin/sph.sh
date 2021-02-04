#!/bin/bash

# to run, use "bash sph.sh"
# to include dust, use -d option: "bash sph.sh -d"
# to specify project name, use -n: "bash sph.sh -n project_name"
# if no name is specified, will use name_default as project name

name_default="sph_face_nodust"

while getopts "n:d" opt
do
   case "$opt" in
      n ) name="$OPTARG" ;;
      d ) dust="True" ;;
   esac
done

if [ -z ${name+x} ]; then name="$name_default"; else echo "name is set to '$name'"; fi

echo project name is "$name"

mainPath="/mount/owl1/ntf229/fit_simulated_SED"
#projectPath="/mount/owl1/ntf229/fit_simulated_SED_projects/$name" # must contain config.txt (see ski_file_reader.py)
projectPath="/mount/owl1/ntf229/fit_simulated_SED_projects/GSWLC-1/$name" # must contain config.txt (see ski_file_reader.py)

echo project path is "$projectPath"

# make directories if they don't already exist
#mkdir -p $projectPath/SKIRT_files
mkdir -p $projectPath/Prospector_files
mkdir -p $projectPath/Analysis

# make text files from NIHAO data
#python $mainPath/python/fit_simulated_sed/txtFiles.py --path="$projectPath"

if [ "$dust" == "True" ]; then
  echo "Including dust"
else
  rm $projectPath/SKIRT_files/dust.txt
  touch $projectPath/SKIRT_files/dust.txt
  echo "Created empty dust.txt file"
fi

# move ski file to current project
#cp $mainPath/ski_files/sph.ski $projectPath/SKIRT_files/$name.ski

# change values in newly created .ski file 
#python $mainPath/python/fit_simulated_sed/ski_file_reader.py --filename="$name".ski --projectPath="$projectPath"

#cd $projectPath/SKIRT_files # need to cd here for outputs to be in right place
#skirt $name.ski 
#python -m pts.do plot_seds . 
#cd -

#mv $projectPath/SKIRT_files/wave.npy $projectPath/Prospector_files/wave.npy
#mv $projectPath/SKIRT_files/spec.npy $projectPath/Prospector_files/spec.npy

if [ -f $projectPath/Prospector_files/fit.h5 ] ; then
    rm $projectPath/Prospector_files/fit.h5
    echo removed fit file 
fi

python $mainPath/python/fit_simulated_sed/params.py --emcee --outfile=fit --path=$projectPath
python $mainPath/python/fit_simulated_sed/compare.py --filename=fit.h5 --path=$projectPath
python $mainPath/python/fit_simulated_sed/contour.py --filename=fit.h5 --path=$projectPath



