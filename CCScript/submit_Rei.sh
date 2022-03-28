#!/bin/bash
#SBATCH --ntasks-per-node=1
#SBATCH --cpus-per-task=4
#SBATCH --time=9:00:00
#SBATCH --mem=50G

#SBATCH --mail-user=rei.katsuta@mail.utoronto.ca
#SBATCH --mail-type=BEGIN
#SBATCH --mail-type=END
#SBATCH --mail-type=FAIL
#SBATCH --mail-type=REQUEUE
#SBATCH --mail-type=ALL


python3 ../RunSimulationScript.py