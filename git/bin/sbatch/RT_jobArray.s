#!/bin/bash

#SBATCH --nodes=1
#SBATCH --ntasks-per-node=1
#SBATCH --cpus-per-task=40
#SBATCH --time=10:00:00
#SBATCH --mem=60GB
#SBATCH --job-name=RTbig_inc0,10,20,30,40,50,60,70,80,90_wave30_3e7
#SBATCH --mail-type=END
#SBATCH --output=slurm_out/slurm_%x_%a.out
#SBATCH --array=0,10,20,30,40,50,60,70,80,90

module purge

cd /home/ntf229/containers

singularity exec --overlay overlay-15GB-500K.ext3:ro \
/scratch/work/public/singularity/cuda11.0-cudnn8-devel-ubuntu18.04.sif \
/bin/bash -c 'source /ext3/env.sh; \
python /home/ntf229/RT_fit/git/bin/justRT.py \
--dust="True" --inc="$SLURM_ARRAY_TASK_ID" --maxLevel="7" --wavelengths="30" --numPhotons="3e7" --pixels="2000"'



