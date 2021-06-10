"""
This is the simulation demo program, take in the argument user put in and call appropriate function to generate
appropriate parameter and run the simulation and output the result into file
"""
import numpy as np

import Bacteria
import Film


class Simulation():
    """
    This class is used for simulation
    """

    def __init__(self, film: Film, bacteria: Bacteria, simulationType: str):
        """
        Init the simulation
        :param film: The film want to simulation
        :param bacteria: The bacteria want to put on the film to do the simulation
        :param simulationType: The type of simulation want
        """
        self.film = film
        self.bacteria = bacteria
        self.type = simulationType

    def simulate(self, interval_x, interval_y):
        """
        This is the main function in this program, call function do the simulation and output the result
        """
        pass


    def output(self):
        """
        Output the simulation result into a file
        """
        pass

    def _interact(self, interval_x, interval_y):
        pass