class SimulationException(Exception):
    
    def __init__(self, message):
        super().__init__(message)

class SimulationParameterException(SimulationException):
    
    def __init__(self, param_name):
        super().__init__("Error occured while parsing parameter: " + param_name)
