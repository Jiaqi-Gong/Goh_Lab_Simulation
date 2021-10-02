"""
This program is used to run the simulation, but do not check the validity of parameter
"""
import sys
import time
import traceback

from SimulatorFile.Dynamic import DynamicSimulator
from SimulatorFile.EnergyScan import EnergySimulator
from ExternalIO import *


def runSimulation():
    # get log file
    write_at_end = True
    write_log = True
    generate_image = True

    message = setIndicator(generate_image, write_log, write_at_end)
    showMessage(message)

    showMessage("WARNING: validity of parameter uses is not check, use runSimulationCmd to check the validity of "
                "parameter uses")

    time.sleep(1)

    # simulator info
    simulationType = 1
    trail = 999
    dimension = 2
    simulatorType = 1
    interactType = "DOT"
    # interactType = "CUTOFF"

    # film info
    filmSeed = 1
    if dimension == 2:
        filmSurfaceSize = (10000, 10000)
    elif dimension == 3:
        filmSurfaceSize = (1000, 1000, 1)  # For film surface, z value should be 1, since the film is just a surace, the thickness of it should be 1
    else:
        raise RuntimeError("Unknown dimension: {}".format(dimension))
    filmSurfaceShape = "rectangle"
    filmNum = 1
    bacteriaNum = 5
    interval_x = 10
    interval_y = 10
    filmSurfaceCharge = +1
    filmDomainSize = (6, 6)
    filmDomainShape = "diamond"
    filmNeutralDomain = True
    filmDomainCon = 0.2  # if need to change charge ratio, change this
    filmDomainChargeConcentration = 0.5  # ignore

    # bacteria info
    bacteriaSeed = 10
    if dimension == 2:
        bacteriaSize = (100, 100)
        bacteriaSurfaceShape = "rectangle"
    elif dimension == 3:
        bacteriaSize = (100, 100, 5)  # For bacteria, z value is the height of bacteria, can be any number
        bacteriaSurfaceShape = "cuboid"
    else:
        raise RuntimeError("Unknown dimension: {}".format(dimension))

    bacteriaSurfaceCharge = -1
    bacteriaDomainSize = (10, 10)
    bacteriaDomainShape = "diamond"
    bacteriaDomainCon = 0.2
    bacteriaDomainChargeConcentration = 0.5  # ignore
    bacteriaNeutralDomain = True

    cutoff = 3

    # below are for dynamic simulation
    probabilityType = "SIMPLE"
    timestep = 1000
    Lambda = 10
    simple = 0.1
    bacteriaMovementSeed = 10
    unstuck = False
    unstuckProbability = 0.001

    # take info for simulator
    if simulatorType == 1:
        simulator = EnergySimulator
        # taking info for energy scan simulation
        parameter = {"interactType": interactType, "simulationType": simulationType, "cutoff": cutoff}

    elif simulatorType == 2:
        simulator = DynamicSimulator

        # taking info for dynamic simulation
        parameter = {"probabilityType": probabilityType, "timeStep": timestep, "dumpStep": 1,
                     "bacteriaMovementSeed": bacteriaMovementSeed, "unstuck": unstuck,
                     "unstuckProbability": unstuckProbability}

        if probabilityType.upper() == "SIMPLE":
            parameter["probability"] = simple
        elif probabilityType.upper() == "POISSON":
            parameter["Lambda"] = Lambda
    else:
        raise RuntimeError("Unknown simulator type: {}".format(simulatorType))

    # generate simulator
    try:
        sim = simulator(trail, dimension,
                    filmSeed, filmSurfaceSize, filmSurfaceShape, filmSurfaceCharge,
                    filmDomainSize, filmDomainShape, filmDomainCon, filmDomainChargeConcentration,
                    bacteriaSeed, bacteriaSize, bacteriaSurfaceShape, bacteriaSurfaceCharge,
                    bacteriaDomainSize, bacteriaDomainShape, bacteriaDomainCon, bacteriaDomainChargeConcentration,
                    filmNum, bacteriaNum, interval_x, interval_y, filmNeutralDomain, bacteriaNeutralDomain, parameter)

        sim.runSimulate()
        closeLog()
    except Exception as e:
        exc_type, exc_value, exc_traceback = sys.exc_info()
        info = ""
        info += str('e.message: {}\t'.format(exc_value))
        info += str("Note, object e and exc of Class %s is %s the same." % (type(exc_value), ('not', '')[exc_value is e]))
        info += str('traceback.print_exc(): {}'.format( traceback.print_exc()))
        info += str('traceback.format_exc():\n%s' % traceback.format_exc())
        writeLog(info)
        closeLog()
        exit(1)


if __name__ == '__main__':
    runSimulation()
