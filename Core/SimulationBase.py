from Logging.Logging import SimLogger as Logger, LogLevel
from Core.Parameters import SimulationParameters, SimulationParameter, ParameterValidation as PV
from Statistics.Statistics import StatisticsCollection
import simpy
import random
from enum import IntEnum

"""
    Simulation base class.

    Handles common properties shared between different simulations, including:
    - Parameters parsing (adding common parameters to supported parameters).
    - Initializing logging and statistics modules.
    - Initializing RNG.
    - Wraps simpy dependency.

"""


class LogOutput(IntEnum):
    """
        Enum to simplify logging output parameter.
    """
    LOG_NONE   = 0
    LOG_STDOUT = 2
    LOG_FILE   = 4
    LOG_BOTH   = 8




class SimulationBase(object):
    """
        Simulation base class.
    """
    
    COMMON_PARAMS = { "log-level":       SimulationParameter("Log level: DEBUG, INFO, WARNING, ERROR or CRITICAL.", "INFO", PV.validate_enum, LogLevel),
                      "log-out":         SimulationParameter("Log output: LOG_NONE, LOG_STDOUT, LOG_FILE or LOG_BOTH. LOG_BOTH will output log into stdout and file both.", "LOG_BOTH", PV.validate_enum, LogOutput),
                      "simulation-time": SimulationParameter("Simulation time in hours.", 10, PV.validate_integer, 0),
                      "random-seed":     SimulationParameter("Seed for random number generator.", 1, PV.validate_integer, 0),
                      "result-folder":   SimulationParameter("Folder to store simulation results.", "./", PV.validate_folder),
                     }

    def __init__(self, supported_parameters):
        
        # Store supported parameters (merged with common parameters):
        self.supported_parameters = z = {**SimulationBase.COMMON_PARAMS, **supported_parameters}
        self.parameters = None
        self._simulation = simpy.Environment()


    def create(self, lines, log_stdout=True):
        """
            Parses simulation parameters.
        """
        self.parameters = SimulationParameters(lines, self.supported_parameters)

        # Initialize logger with requested log level and log all used parameters:
        Logger(self.parameters["log-level"], self._simulation, stdout=self.parameters["log-out"] & 10, file = str(self.parameters["result-folder"]) + "/log.log" if self.parameters["log-out"] & 12 else None)
        Logger.log(LogLevel.INFO, "Starting simulation with following parameters:\n" + 
                   "\n".join(["{:30} {}".format(p, self.parameters[p]) for p in self.supported_parameters]))

        # Initialize statistics:
        StatisticsCollection()

        # Initialize RNG:
        random.seed(self.parameters["random-seed"])


    def run(self, entry_func, *args):
        """
            Starts simulation from <entry_func> method with additional parameters <*args>.
        """
        self._simulation.process(entry_func(self._simulation, *args))
        self._simulation.run(until=self.parameters["simulation-time"])


    def create_resource(self, capacity):
        Logger.log(LogLevel.DEBUG, "Created simulation resource sized " + str(capacity) + ".")
        return simpy.Resource(self._simulation, capacity=capacity)


    def print_supported_parameters(self):
        """
            Prints all the supported parameters and default values.
        """
        print("\n".join(["{:30} {} Defaults to: {}.".format(param[0], param[1].get_description(), param[1].get_default_value()) for param in self.supported_parameters.items()]))
