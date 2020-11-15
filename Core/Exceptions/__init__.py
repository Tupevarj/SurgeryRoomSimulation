

class SimulationException(Exception):
    pass

class SimulationParameterException(SimulationException):
    
    def __init__(self, param_name):
        super().__init__("Error occured while parsing parameter: " + param_name)
