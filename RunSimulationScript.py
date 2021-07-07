"""
This program is used to run the simulation, but do not check the validity of parameter
"""
import time

from SimulatorFile.Dynamic import DynamicSimulator
from SimulatorFile.EnergyScan import EnergySimulator
from ExternalIO import openLog, showMessage


def runSimulation():
    # get log file
    openLog()

    showMessage("WARNING: validity of parameter uses is not check, use runSimulationCmd to check the validity of "
                "parameter uses")

    time.sleep(3)

    simulationType = 1
    trail = 1
    dimension = 2
    filmSeed = 1
    filmSurfaceSize = (10, 10)
    filmSurfaceShape = "rectangle"
    filmNum = 1
    bacteriaNum = 5
    interval_x = 50
    interval_y = 50
    filmSurfaceCharge = 0
    filmDomainSize = (1, 1)
    filmDomainShape = "cross"
    filmDomainCon = 0.5
    filmDomainChargeConcentration = 0.5
    bacteriaSeed = 10
    bacteriaSize = (5, 5)
    bacteriaSurfaceShape = "rectangle"
    bacteriaSurfaceCharge = 0
    bacteriaDomainSize = (1, 1)
    bacteriaDomainShape = "single"
    bacteriaDomainCon = 0.5
    bacteriaDomainChargeConcentration = 0.5

    ### below is new variable
    simulatorType = 1
    interactType = "DOT"

    # below are for dynamic simulation, we are not using for now
    probabilityType = "POISSON"
    timestep = 1000
    Lambda = 10

    # take info for simulator
    if simulatorType == 1:
        simulator = EnergySimulator
        # taking info for energy scan simulation
        parameter = {"interactType": interactType}

    elif simulatorType == 2:
        simulator = DynamicSimulator
        # taking info for dynamic simulation
        parameter = {"probabilityType": probabilityType, "timestep": timestep}

        if probabilityType.upper() == "POISSON":
            parameter["Lambda"] = Lambda
    else:
        raise RuntimeError("Unknown simulator type")

    # generate simulator
    sim = simulator(simulationType, trail, dimension,
                    filmSeed, filmSurfaceSize, filmSurfaceShape, filmSurfaceCharge,
                    filmDomainSize, filmDomainShape, filmDomainCon, filmDomainChargeConcentration,
                    bacteriaSeed, bacteriaSize, bacteriaSurfaceShape, bacteriaSurfaceCharge,
                    bacteriaDomainSize, bacteriaDomainShape, bacteriaDomainCon, bacteriaDomainChargeConcentration,
                    filmNum, bacteriaNum, interval_x, interval_y, parameter)


    sim.runSimulate()

if __name__ == '__main__':
    runSimulation()
