from Logging.Logging import Logger, LogLevel
from Core.Parameters import SimulationParameters

class SimulatorBase(object):

    def __init__(self, supported_parameters):
        
        # Store supported parameters:
        self.supported_parameters = supported_parameters
        self.parameters = None


    def create(self, lines):
        """
            Creates parameters only for now.
        """
        self.parameters = SimulationParameters(lines, self.supported_parameters)

        # Initialize logger with requested log level and log all used parameters:
        Logger(self.parameters["log-level"])
        Logger.log(LogLevel.INFO, "Starting simulation with following parameters:\n" + 
                   ("\n").join([p + ": " + str(self.parameters[p]) for p in self.supported_parameters]))



    def print_supported_parameters(self):
        pass # TODO:

