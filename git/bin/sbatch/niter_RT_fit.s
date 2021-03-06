#!/bin/bash

#SBATCH --nodes=1
#SBATCH --ntasks-per-node=1
#SBATCH --cpus-per-task=1
#SBATCH --time=15:00:00
#SBATCH --mem=20GB
#SBATCH --job-name=niter4096_RT_fit_wave250_1e8_maxLevel11_GSWLC1_walkers256_e5d
#SBATCH --mail-type=END
#SBATCH --output=slurm_out/slurm_%x.out
#SBATCH --array=0,5,10,15,20,25,30,35,40,45,50,55,60,65,70,75,80,85,90

module purge

cd /home/ntf229/containers

singularity exec --overlay overlay-15GB-500K.ext3:ro \
/scratch/work/public/singularity/cuda11.0-cudnn8-devel-ubuntu18.04.sif \
/bin/bash -c 'source /ext3/env.sh; \
python /home/ntf229/RT_fit/git/bin/niter_RT_fit.py \
--inc="$SLURM_ARRAY_TASK_ID" --dust="True" --maxLevel="11" \
--wavelengths="250" --numPhotons="1e8" --pixels="2000" \
--fitType="GSWLC1" --nwalkers="256" --niter="4096"'



