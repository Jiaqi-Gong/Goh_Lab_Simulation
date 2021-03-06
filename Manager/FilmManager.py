"""
This program:
- Saves the FilmFile.
- Manages all films.
"""
from typing import Tuple, Union

from numpy import ndarray

from SurfaceGenerator.Domain import DomainGenerator
from ExternalIO import showMessage, writeLog, saveSurface
from FilmFile.Film import FilmSurface2D, FilmSurface3D


class FilmManager:
    """
    This class saves all film used in this simulation and generate all corresponding film
    """
    # Declare the type of all variable
    trail: int
    dimension: int
    filmSeed: int
    filmSurfaceSize: Union[Tuple[int, int], Tuple[int, int, int]]
    filmSurfaceShape: str
    filmSurfaceCharge: int
    filmDomainSize: Tuple[int, int]
    filmDomainShape: str
    filmDomainConcentration: float
    filmNum: int
    film: list
    neutralDomain: bool

    def __init__(self, trail: int, dimension: int,
                 filmSeed: int, filmSurfaceSize: Union[Tuple[int, int], Tuple[int, int, int]], filmSurfaceShape: str,
                 filmSurfaceCharge: int, filmDomainSize: Tuple[int, int], filmDomainShape: str,
                 filmDomainConcentration: float, filmDomainChargeConcentration: float, filmNum: int,
                 neutralDomain: bool):
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
        self.neutralDomain = neutralDomain

        # init a variable to store all film
        self.film = []

    def generateFilm(self, generateDomain: bool) -> None:
        """
        This function generate corresponding film need based on the number wanted
        """
        writeLog("This is function generate Film in the FilmManager.py")
        showMessage("Start to generate Film")
        # writeLog(self.__dict__)

        # depends on the dimension to call appropriate function
        for i in range(self.filmNum):
            seed = self.filmSeed + i

            # generate domain generator
            filmDomainGenerator = DomainGenerator(seed, self.neutralDomain)
            if self.dimension == 2:
                self._generate2DFilm(filmDomainGenerator, generateDomain)
            elif self.dimension == 3:
                self._generate3DFilm(filmDomainGenerator, generateDomain)
            else:
                raise RuntimeError("Unknown dimension in film manager")

            # save this surface
            info = [self.filmSeed, self.filmSurfaceSize, self.filmSurfaceShape, self.filmNum, self.filmSurfaceCharge,
                    self.filmDomainSize, self.filmDomainShape, self.neutralDomain, self.filmDomainConcentration,
                    self.filmDomainChargeConcentration, self.film[-1]]

            # create file name
            file_name = ""
            for i in info[:-1]:
                file_name += str(i)
                file_name += "_"

            saveSurface(info, file_name[:-1])

    def _generate2DFilm(self, domainGenerator: DomainGenerator, generateDomain: bool) -> None:
        """
        Generates 2D film
        """
        showMessage("Generating 2D film...")
        # generate 2D Film Surface
        film = FilmSurface2D(self.trail, self.filmSurfaceShape, self.filmSurfaceSize, self.filmSurfaceCharge,
                             domainGenerator.seed)

        if generateDomain:
            showMessage("Generating 2D film with domain...")
            film.surfaceWithDomain, film.realDomainConc = domainGenerator.generateDomain(film, self.filmDomainShape,
                                                                                     self.filmDomainSize,
                                                                                     self.filmDomainConcentration,
                                                                                     self.filmDomainChargeConcentration)
        else:
            film.surfaceWithDomain, film.realDomainConc = film, 0.0

        # save the film into manager
        self.film.append(film)

        # write into log
        showMessage("2D film generation: Complete.")
        writeLog(self.film)

    def _generate3DFilm(self, domainGenerator: DomainGenerator, generateDomain: bool) -> None:
        """
        Generates 3D film
        """
        showMessage("Generating 3D film...")
        # generate 3D Film Surface
        film = FilmSurface3D(self.trail, self.filmSurfaceShape, self.filmSurfaceSize, self.filmSurfaceCharge,
                             domainGenerator.seed)

        if generateDomain:
            showMessage("Generating 3D film with domain...")
            film.surfaceWithDomain, film.realDomainConc = domainGenerator.generateDomain(film, self.filmDomainShape,
                                                                                     self.filmDomainSize,
                                                                                     self.filmDomainConcentration,
                                                                                     self.filmDomainChargeConcentration)
        else:
            film.surfaceWithDomain, film.realDomainConc = film, 0.0

        # save the film into manager
        self.film.append(film)

        # write into log
        showMessage("3D film generation: Complete.")
        writeLog(self.film)

    def setSurface(self, surface: ndarray) -> None:
        """
        This function read in the pre-generated surface structure
        :param surface: a pre-generated surface structure
        """
        self.film.append(surface)
