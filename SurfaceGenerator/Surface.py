"""
This program is generating the surface for test
"""
import abc
from typing import Tuple, Union
from numpy import ndarray

# follow constant is for surface, but overwrite by the size passed in, can ignore
# this can be change, balance the resolution and the time cost

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
    dimension: int
    surfaceCharge: int
    originalSurface: ndarray
    surfaceWithDomain: Union[None, ndarray]

    @abc.abstractmethod
    def __init__(self, trail: int, shape: str, size: Tuple[int, int], seed: int, surfaceCharge: int, dimension: int) \
            -> None:
        """
        Init this surface
        1micrometer = 100 points
        :param trail: trail number
        :param shape: shape of this surface
        :param size: size of the surface, in the format ###x###, in unit micrometer, 1micrometer = 100 points
        :param seed: seed used to generate this film with domain
        """

        # set other information about this surface
        # 1 micrometer = 100 points
        self.length = size[0] * 100
        self.width = size[1] * 100
        self.trail = trail
        self.shape = shape
        self.seed = seed

        # set the surface dimension
        self.dimension = dimension

        # set the surface charge
        # -1 for negative, 0 for neutral, 1 for positive
        self.surfaceCharge = surfaceCharge

        # generate surface
        self.originalSurface = self._generateSurface()

        # Init the surface
        self.surfaceWithDomain = None

    @abc.abstractmethod
    def _generateSurface(self) -> ndarray:
        """
        Generate the corresponding surface, override in subclass
        """
        raise NotImplementedError

    def importSurface(self, filepath: str) -> ndarray:
        """
        This function read in the pre-generated surface structure
        :param filepath: file path to the surface structure want to import
        """

        # should be implement here, but not done for now
        raise NotImplementedError
