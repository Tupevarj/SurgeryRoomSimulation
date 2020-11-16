from Logging.Logging import Logger, LogLevel
from Core.Parameters import SimulationParameters, SimulationParameter, validate_enum, validate_integer
import simpy

class SimulatorBase(object):
    
    COMMON_PARAMS = { "log-level":        SimulationParameter("INFO", validate_enum, LogLevel),
                       "simulation-time": SimulationParameter(10, validate_integer, 0),
                       "random-seed":     SimulationParameter(1, validate_integer, 0)
                     }

    def __init__(self, supported_parameters):
        
        # Common parameters:

        # Store supported parameters:
        self.supported_parameters = z = {**SimulatorBase.COMMON_PARAMS, **supported_parameters}
        self.parameters = None
        self._simulation = simpy.Environment()


    def create(self, lines):
        """
            Creates parameters only for now.
        """
        self.parameters = SimulationParameters(lines, self.supported_parameters)

        # Initialize logger with requested log level and log all used parameters:
        Logger(self.parameters["log-level"])
        Logger.log(LogLevel.INFO, "Starting simulation with following parameters:\n" + 
                   ("\n").join([p + ": " + str(self.parameters[p]) for p in self.supported_parameters]))


    def run(self):
        self._simulation.run(until=self.parameters["simulation-time"])

    def print_supported_parameters(self):
        pass # TODO:

