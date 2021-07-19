"""
This program is used to run the simulation, but do not check the validity of parameter
"""
import time

from SimulatorFile.Dynamic import DynamicSimulator
from SimulatorFile.EnergyScan import EnergySimulator
from ExternalIO import openLog, showMessage


def runSimulation():
    # get log file
    log_name = openLog()
    showMessage(log_name)

    showMessage("WARNING: validity of parameter uses is not check, use runSimulationCmd to check the validity of "
                "parameter uses")

    time.sleep(3)

    # simulator info
    simulationType = 1
    trail = 41
    dimension = 3
    simulatorType = 2
    interactType = "DOT"
    # interactType = "CUTOFF"

    # film info
    filmSeed = 1
    if dimension == 2:
        filmSurfaceSize = (1000, 1000)
    elif dimension == 3:
        filmSurfaceSize = (1000, 1000, 1)  # For film surface, z value should be 1, since the film is just a surace, the thickness of it should be 1
    filmSurfaceShape = "rectangle"
    filmNum = 1
    bacteriaNum = 100
    interval_x = 10
    interval_y = 10
    filmSurfaceCharge = -1
    filmDomainSize = (100, 100)
    filmDomainShape = "diamond"
    filmNeutralDomain = False
    filmDomainCon = 0.5  # if need to change charge ratio, change this
    filmDomainChargeConcentration = 0.5  # ignore

    # bacteria info
    bacteriaSeed = 10
    if dimension == 2:
        bacteriaSize = (20, 20)
    elif dimension == 3:
        bacteriaSize = (50, 50, 5)  # For bacteria, z value is the height of bacteria, can be any number
    bacteriaSurfaceShape = "cuboid"
    bacteriaSurfaceCharge = 1
    bacteriaDomainSize = (4, 4)
    bacteriaDomainShape = "diamond"
    bacteriaDomainCon = 0.5
    bacteriaDomainChargeConcentration = 0.5  # ignore
    bacteriaNeutralDomain = False

    # below are for dynamic simulation
    probabilityType = "SIMPLE"
    timestep = 1000
    Lambda = 10
    simple = 0.1
    bacteriaMovementSeed = 10

    # take info for simulator
    if simulatorType == 1:
        simulator = EnergySimulator
        # taking info for energy scan simulation
        parameter = {"interactType": interactType, "simulationType": simulationType, "cutoff": 6}

    elif simulatorType == 2:
        simulator = DynamicSimulator
        # taking info for dynamic simulation
        parameter = {"probabilityType": probabilityType, "timeStep": timestep, "dumpStep": 1,
                     "bacteriaMovementSeed": bacteriaMovementSeed}

        if probabilityType.upper() == "SIMPLE":
            parameter["probability"] = simple
        elif probabilityType.upper() == "POISSON":
            parameter["Lambda"] = Lambda
    else:
        raise RuntimeError("Unknown simulator type")

    # generate simulator
    sim = simulator(trail, dimension,
                    filmSeed, filmSurfaceSize, filmSurfaceShape, filmSurfaceCharge,
                    filmDomainSize, filmDomainShape, filmDomainCon, filmDomainChargeConcentration,
                    bacteriaSeed, bacteriaSize, bacteriaSurfaceShape, bacteriaSurfaceCharge,
                    bacteriaDomainSize, bacteriaDomainShape, bacteriaDomainCon, bacteriaDomainChargeConcentration,
                    filmNum, bacteriaNum, interval_x, interval_y, filmNeutralDomain, bacteriaNeutralDomain, parameter)

    sim.runSimulate()


if __name__ == '__main__':
    runSimulation()
