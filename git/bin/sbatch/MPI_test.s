#!/bin/bash

#SBATCH --nodes=1
#SBATCH --ntasks-per-node=1
#SBATCH --cpus-per-task=4
#SBATCH --time=1:00:00
#SBATCH --mem=1GB
#SBATCH --job-name=MPI_test
#SBATCH --mail-type=END
#SBATCH --output=slurm_out/slurm_%x.out
#SBATCH --array=0

module purge

for e in $(env | grep SLURM_ | cut -d= -f1 | grep -v SLURM_ARRAY_TASK_ID); do unset $e; done

cd /home/ntf229/containers

singularity exec --overlay overlay-15GB-500K.ext3:ro \
/scratch/work/public/singularity/cuda11.0-cudnn8-devel-ubuntu18.04.sif \
/bin/bash -c 'source /ext3/env.sh; \
python /home/ntf229/RT_fit/git/bin/call_mpi_hello_world.py'



