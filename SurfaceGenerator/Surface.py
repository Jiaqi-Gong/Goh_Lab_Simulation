"""
This program is generating the surface for test
"""
import abc

# follow constant is for surface, but overwrite by the size passed in, can ignore
# this can be change, balance the resolution and the time cost
from typing import Tuple

X_AX = 10500  # number of coordinates for x-axis
Y_AX = 10500  # number of coordinates for y-axis
Z_AX_2D = 3  # number of coordinates for z-axis for 2D


class Surface:
    """
    This is an abstract class for surface
    charge can be negative -1, neutral 0, positive 1
    1micrometer = 100 points
    """
    # Declare the type of all variable
    length: int
    width: int
    trail: int
    shape: str
    seed: int


    @abc.abstractmethod
    def __init__(self, trail: int, shape: str, size: Tuple[int, int], seed:int) -> None:
        """
        Init this surface
        1micrometer = 100 points
        :param trail: trail number
        :param shape: shape of this surface
        :param size: size of the surface, in the format ###x###, in unit micrometer, 1micrometer = 100 points
        """

        # set other information about this surface
        # 1micrometer = 100 points
        self.length = size[0] * 100
        self.width = size[1] * 100
        self.trail = trail
        self.shape = shape
        self.originalSurface = self._generateSurface()
        self.seed = seed

        # Init the surface
        self.surfaceWithDomain = None

    def _generateSurface(self) -> None:
        """
        Generate the corresponding surface, override in subclass
        """
        print("Start to generating surface with shape: ", self.shape)

        # generate corresponding shape
        if self.shape.upper() == "RECTANGLE" or self.shape.upper() == "CUBOID":
            return self._generateRec()

    @abc.abstractmethod
    def _generateRec(self) -> None:
        """
        This function generate rectangle shape for 2D, cuboid for 3D, should be implement in the subclass
        """
        raise NotImplementedError

    def importSurface(self, filepath: str) -> None:
        """
        This function read in the pre-generated surface structure
        :param filepath: file path to the surface structure want to import
        """

        # should be implement here, but not done for now
        raise NotImplementedError
