
"""
    Simulation exceptions.
"""

class SimulationException(Exception):
    """
        Base class for simulation exceptions.
    """
    def __init__(self, message):
        super().__init__(message)

class SimulationParameterException(SimulationException):
    """
        Class for parameter parsing simulation exceptions.
    """
    def __init__(self, param_name):
        super().__init__("Error occured while parsing parameter: " + param_name)
