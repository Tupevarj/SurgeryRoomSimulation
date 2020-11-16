from Logging import Logger, LogLevel, LoggingBase
from Core.Modules import SimulationParameters

class SimulationBase(LoggingBase):

    def __init__(self, supported_parameters):

        self.supported_parameters = supported_parameters
        self.parameters = None


    def create(self, lines):
        """
            Creates parameters only for now.
        """
        self.parameters = SimulationParameters(lines, self.supported_parameters)


