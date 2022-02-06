#!/bin/bash
#SBATCH --ntasks-per-node=1
#SBATCH --cpus-per-task=21
#SBATCH --time=24:00:00
#SBATCH --mem=15G

#SBATCH --mail-user=jiaqi.gong@mail.utoronto.ca
#SBATCH --mail-type=BEGIN
#SBATCH --mail-type=END
#SBATCH --mail-type=FAIL
#SBATCH --mail-type=REQUEUE
#SBATCH --mail-type=ALL

source ../ENV/bin/activate
python3 RunSimulationScript.py
