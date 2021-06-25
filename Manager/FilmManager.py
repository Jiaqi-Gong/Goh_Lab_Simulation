"""
This program is used to save the Film and manage all films
"""
from typing import Tuple

from SurfaceGenerator.Domain import DomainGenerator
from ExternalIO import showMessage, writeLog
from Film.Film import FilmSurface2D


class FilmManager:
    """
    This class saves all film used in this simulation and generate all corresponding film
    """
    # Declare the type of all variable
    trail: int
    dimension: int
    filmSeed: int
    filmSurfaceSize: Tuple[int, int]
    filmSurfaceShape: str
    filmSurfaceCharge: int
    filmDomainSize: Tuple[int, int]
    filmDomainShape: str
    filmDomainconcentration: float
    filmNum: int
    film: list


    def __init__(self, trail: int, dimension: int,
                 filmSeed: int, filmSurfaceSize: Tuple[int, int], filmSurfaceShape: str, filmSurfaceCharge: int,
                 filmDomainSize: Tuple[int, int], filmDomainShape: str, filmDomainConcentration: float, filmDomainChargeConcentration: float, filmNum: int):
        """
        Init the film manager, take in the
        """
        # set film variable
        self.trail = trail
        self.dimension = dimension

        # set film variable
        self.filmSeed = filmSeed
        self.filmNum = filmNum
        self.filmSurfaceSize = filmSurfaceSize
        self.filmSurfaceShape = filmSurfaceShape
        self.filmSurfaceCharge = filmSurfaceCharge
        self.filmDomainSize = filmDomainSize
        self.filmDomainShape = filmDomainShape
        self.filmDomainConcentration = filmDomainConcentration
        self.filmDomainChargeConcentration = filmDomainChargeConcentration

        # init a variable to store all film
        self.film = []

    def generateFilm(self):
        """
        This function generate corresponding film need based on the number wanted
        """
        writeLog("This is function generate Film in the FilmManager.py")
        showMessage("Start to generate Film")
        writeLog(self.__dict__)

        # depends on the dimension to call appropriate function
        if self.dimension == 2:
            for i in range(self.filmNum):
                seed = self.filmSeed + i

                # generate domain generator
                filmDomainGenerator = DomainGenerator(seed)
                self._generate2DFilm(filmDomainGenerator)

        elif self.dimension == 3:
            raise NotImplementedError

    def _generate2DFilm(self, domainGenerator: DomainGenerator):
        """
        Generate 2D film
        """
        showMessage("Generate 2D film")
        # generate 2D Film Surface
        film = FilmSurface2D(self.trail, self.filmSurfaceShape, self.filmSurfaceSize, self.filmSurfaceCharge,
                             domainGenerator.seed)

        showMessage("Generate 2D film with domain")
        film.surfaceWithDomain = domainGenerator.generateDomain(film, self.filmDomainShape, self.filmDomainSize,
                                                                self.filmDomainConcentration, self.filmDomainChargeConcentration)

        # save the film into manager
        self.film.append(film)

        # write into log
        showMessage("2D film generate done")
        writeLog(self.film)
