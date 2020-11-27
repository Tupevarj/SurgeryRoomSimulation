from enum import Enum
import random
import ast

"""
    Distribution Module


    Wrapper class for random number generation.
    - Allow to set seed globally.
    - Eases to change underlying generator.

"""

class Distribution(Enum):
    EXPONENTIAL = 0,
    UNIFORM     = 1


class RandomGenerator:
    """
        Singleton class to control random number generation. Makes parameterized seed
        globally available between individual random number generators.
    """
    __instance = None
    
    def __new__(cls, seed):
        """
            Creates singleton instance (first call only).
        """
        if RandomGenerator.__instance is None:
            RandomGenerator.__instance = object.__new__(cls)
        RandomGenerator.__instance.__seed = seed
        return RandomGenerator.__instance


    @staticmethod
    def new_generator():
        """
            Create new RNG.
        """
        return random.Random(RandomGenerator.__instance.__seed)


class Rng:
    """
        Random number generator created from common seed set in RandomGenerator.
        Supports exponential and uniform random streams.
    """

    def __init__(self, string):
        args = ast.literal_eval(string)
        distribution = Distribution[args[0]]
        self.__rng = None
        if Distribution[args[0]] is Distribution.EXPONENTIAL:
            self.__next = self.__get_exponential
            self.__expo = 1.0 / float(args[1])
        else:
            self.__next = self.__get_uniform
            self.__min = float(args[1])
            self.__max = float(args[2])

    def initialize(self):
        """
            Initializes the generator. NOTE: Needs to be called before
            calling next().
        """
        self.__rng = RandomGenerator.new_generator()
        return self

    def next(self):
        """
            Gets next random number.
        """
        return self.__next()

    def __get_exponential(self):
        return self.__rng.expovariate(self.__expo)

    def __get_uniform(self):
        return self.__rng.uniform(self.__min, self.__max)

