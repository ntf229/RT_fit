#!/bin/bash

#SBATCH --nodes=1
#SBATCH --ntasks-per-node=1
#SBATCH --cpus-per-task=40
#SBATCH --time=4:00:00
#SBATCH --mem=60GB
#SBATCH --job-name=RT_e2d_wave30_1e6_maxLevel11_500px
#SBATCH --mail-type=END
#SBATCH --output=slurm_out/slurm_%x.out

module purge

cd /home/ntf229/containers

singularity exec --overlay overlay-15GB-500K.ext3:ro \
/scratch/work/public/singularity/cuda11.0-cudnn8-devel-ubuntu18.04.sif \
/bin/bash -c 'source /ext3/env.sh; \
python /home/ntf229/RT_fit/git/bin/RT_e2d.py \
--dust="True" --maxLevel="11" --wavelengths="30" --numPhotons="1e6" --pixels="500"'



