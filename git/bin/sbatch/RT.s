#!/bin/bash

#SBATCH --nodes=1
#SBATCH --ntasks-per-node=1
#SBATCH --cpus-per-task=1
#SBATCH --time=30:00:00
#SBATCH --mem=10GB
#SBATCH --job-name=RT_inc0_wave30_3e7_maxLevel12
#SBATCH --mail-type=END
#SBATCH --output=slurm_out/slurm_%x.out

module purge

cd /home/ntf229/containers

singularity exec --overlay overlay-15GB-500K.ext3:ro \
/scratch/work/public/singularity/cuda11.0-cudnn8-devel-ubuntu18.04.sif \
/bin/bash -c 'source /ext3/env.sh; \
python /home/ntf229/RT_fit/git/bin/justRT.py \
--dust="True" --inc="0" --maxLevel="12" --wavelengths="30" --numPhotons="3e7" --pixels="2000"'



