#!/bin/bash

#SBATCH --nodes=1
#SBATCH --ntasks-per-node=1
#SBATCH --cpus-per-task=1
#SBATCH --time=24:00:00
#SBATCH --mem=40GB
#SBATCH --job-name=galaxy_RT_fit_firstBatch_maxLevel13_3e8_g5.55e11
#SBATCH --mail-type=END
#SBATCH --output=slurm_out/slurm_%x.out
#SBATCH --mail-user=ntf229@nyu.edu
#SBATCH --array=11

module purge

galaxies=( 'g1.12e12' 'g1.92e12' 'g2.39e11' 'g2.79e12' 'g3.23e11' 'g3.49e11' 'g3.59e11' 'g3.61e11'
	   'g5.31e11' 'g5.36e11' 'g5.38e11' 'g5.55e11' 'g7.08e11' 'g7.44e11' 'g8.26e11' 'g8.28e11' )

cd /home/ntf229/containers

singularity exec --overlay overlay-15GB-500K.ext3:ro \
	    /scratch/work/public/singularity/cuda11.0-cudnn8-devel-ubuntu18.04.sif \
/bin/bash -c "source /ext3/env.sh; 
python /home/ntf229/RT_fit/git/bin/galaxy_RT_fit.py \
--inc=0 --dust=True --maxLevel=13 \
--wavelengths=250 --numPhotons=3e8 --pixels=2000 \
--fitType=DustPedia --nwalkers=256 --niter=2048 --galaxy=${galaxies[$SLURM_ARRAY_TASK_ID]}"



