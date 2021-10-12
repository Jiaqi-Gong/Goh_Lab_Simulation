"""
This program:
- Generates the surface for tests
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
    realDomainConc: Tuple[float, float]

    @abc.abstractmethod
    def __init__(self, trail: int, shape: str, size: Tuple[int, int, int], seed: int, surfaceCharge: int, dimension: int) \
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
        self.length = size[0]
        self.width = size[1]

        # Not sure does height need to times 100?
        # if height needs to times 100, need to change the height of film put in
        # self.height = size[2] * 100
        self.height = size[2]

        self.trail = trail
        self.shape = shape
        self.seed = seed

        # set real domain concentration
        self.realDomainConc = (-1, -1)

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

