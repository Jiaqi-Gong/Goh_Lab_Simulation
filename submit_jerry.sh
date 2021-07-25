#!/bin/bash
#SBATCH --account=def-aspuru
#SBATCH --ntasks-per-node=1
#SBATCH --cpus-per-task=28
#SBATCH --time=6:00:00
#SBATCH --mem=187G

#SBATCH --mail-user=jerryjh.gu@mail.utoronto.ca
#SBATCH --mail-type=BEGIN
#SBATCH --mail-type=END
#SBATCH --mail-type=FAIL
#SBATCH --mail-type=REQUEUE
#SBATCH --mail-type=ALL

python3 RunSimulationScript.py