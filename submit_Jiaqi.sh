#!/bin/bash
#SBATCH --ntasks-per-node=1
#SBATCH --cpus-per-task=16
#SBATCH --time=16:00:00
#SBATCH --mem=128G

#SBATCH --mail-user=jiaqi.gong@mail.utoronto.ca
#SBATCH --mail-type=BEGIN
#SBATCH --mail-type=END
#SBATCH --mail-type=FAIL
#SBATCH --mail-type=REQUEUE
#SBATCH --mail-type=ALL


python3 RunSimulationScript.py