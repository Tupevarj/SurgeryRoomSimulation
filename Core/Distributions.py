import random

"""
    Wrapper class for random number generation.
    - Allow to set seed globally.
    - Eases to change underlying generator.

"""

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