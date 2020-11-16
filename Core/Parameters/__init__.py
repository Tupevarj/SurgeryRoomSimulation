import re
import sys
from Core.Exceptions import SimulationParameterException
from Core.Module import ModuleBase
from Logging import LogLevel


def validate_integer(string, min = 0, max = sys.maxsize):

    try:
        value = int(string)
        if value >= min and value <= max:
            return value
    except:
        pass

    return None


class SimulationParameter:
    """
        Class for single parameter used in simulator. Contains default value, validator and additional args for validator.
    """
    def __init__(self, default, validator, *args):
        self._validator = validator
        self._default_value = default
        self._args = args


    def get_default_value(self):
        return self._default_value


    def validate(self, string):
        return self._validator(string, *self._args)


class SimulationParameters(ModuleBase):

    SIMULATION_PARAMETERS = { "random-seed":                SimulationParameter(1, validate_integer),
                              "number-of-recovery-places":  SimulationParameter(10, validate_integer, 1, 300),
                              "number-of-operation-places": SimulationParameter(10, validate_integer, 1, 100)}


    def __init__(self, lines):
        """
            Parses parameters from <lines>, where each line is format <PARAMATER_NAME>: <PARAMETER_VALUE>.
        """

        self.LOGGER.log(LogLevel.INFO, "Start parsing parameters.")

        # Fill with defaults:
        self._parameters = self._get_defaults()

        # Parse each line from lines:
        for i in range(len(lines)):
            parameter_fields = self._split_param_line(lines[i])

            # Validate syntax:
            if len(parameter_fields) < 2:
                raise SimulationParameterException("Wrong syntax at line " + str(i) + ".")

            if not parameter_fields[0] in self.SIMULATION_PARAMETERS:
                raise SimulationParameterException("Unknown parameter '" + parameter_fields[0] + "' at line " + str(i) + ".")

            # Parse:
            try:
                parsed = self.SIMULATION_PARAMETERS[parameter_fields[0]].validate(parameter_fields[1])
            except:
                raise SimulationParameterException("Parameter '" + parameter_fields[0] + "' has unvalid typed value at line " + str(i) + ".") 
            
            # Validate parsing:
            if parsed is None:
                raise SimulationParameterException("Parameter '" + parameter_fields[0] + "' has non-valid value at line " + str(i) + ".")   # TODO: Print better explanation

            self._parameters[parameter_fields[0]] = parsed
            self.LOGGER.log(LogLevel.INFO, "Parameter '" + parameter_fields[0] + "' set to: " + str(parsed))
        


    def __getitem__(self, p):
        """
            Returns value of the parameter named <p>.
        """
        return self._parameters[p]


    def _split_param_line(self, line):
        """ 
            Splits line according to syntax: <KEY>: <VALUE>
        """
        return re.split(':\s+', line)


    def _get_defaults(self):
        """
            Returns default values for each supported parameter.
        """
        return {k:v.get_default_value() for k, v in self.SIMULATION_PARAMETERS.items()}

