#!/bin/bash
#SBATCH --ntasks-per-node=1
#SBATCH --cpus-per-task=28
#SBATCH --time=24:00:00
#SBATCH --mem=186G

#SBATCH --mail-user=jiaqi.gong@mail.utoronto.ca
#SBATCH --mail-type=BEGIN
#SBATCH --mail-type=END
#SBATCH --mail-type=FAIL
#SBATCH --mail-type=REQUEUE
#SBATCH --mail-type=ALL


#python3 RunSimulationScript_test.py
python3 test_mp.py >> mp_result.txt