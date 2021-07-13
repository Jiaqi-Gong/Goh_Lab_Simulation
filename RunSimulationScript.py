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
    filmSurfaceCharge = -1
    filmDomainSize = (1, 1)
    filmDomainShape = "octagon"
    filmDomainCon = 0.5
    filmDomainChargeConcentration = 0.5
    bacteriaSeed = 10
    bacteriaSize = (5, 5)
    bacteriaSurfaceShape = "rectangle"
    bacteriaSurfaceCharge = 1
    bacteriaDomainSize = (1, 1)
    bacteriaDomainShape = "octagon"
    bacteriaDomainCon = 0.5
    bacteriaDomainChargeConcentration = 0.5

    ### below is new variable
    simulatorType = 2
    interactType = "DOT"
    # interactType = "CUTOFF"


    # below are for dynamic simulation, we are not using for now
    probabilityType = "SIMPLE"
    timestep = 10
    Lambda = 10
    simple = 0.1
    bacteriaMovementSeed = 10

    # take info for simulator
    if simulatorType == 1:
        simulator = EnergySimulator
        # taking info for energy scan simulation
        parameter = {"interactType": interactType, "simulationType": simulationType, "cutoff": 2}

    elif simulatorType == 2:
        simulator = DynamicSimulator
        # taking info for dynamic simulation
        parameter = {"probabilityType": probabilityType, "timeStep": timestep, "dumpStep": 1,
                     "bacteriaMovementSeed" : bacteriaMovementSeed}

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
                    filmNum, bacteriaNum, interval_x, interval_y, parameter)


    sim.runSimulate()

if __name__ == '__main__':
    runSimulation()
