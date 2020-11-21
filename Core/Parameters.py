import re
import sys
from pathlib import Path
from Core.Exceptions import SimulationParameterException

"""
    Parameters module

    ParameterValidation class holds static methods to validate user provided parameter values.
    SimulationParameter is holder class for single parameter. To add a new parameter, create new
                        instance of this class.

    SimulationParameters handles parameter parsing. Constructor takes list of supported parameters
                         and list of lines containing parseable string. Syntax is:

                         <NAME_OF_PARAMETER1>: <VALUE_OF_PARAMETER1>
                         <NAME_OF_PARAMETER1>: <VALUE_OF_PARAMETER1>

                         .Each parameter should be in it's own line. Line comments starting with
                         '#' character and empty spaces are allowed.
"""

class ParameterValidation:
    """
        Parameter parsing and validation methods.
    """

    @staticmethod
    def validate_enum(string, enum):
        """
            Checks that given <string> is valid enum of type <enum>. 
            Return enum value if valid, otherwise None is returned.
        """
        try:
            return enum[string], ""
        except:
            return None, "Given value is not type of {}.".format(enum)

        
    @staticmethod
    def validate_integer(string, min = 0, max = sys.maxsize):
        """
            Checks that given <string> is valid integer and between <min> and <max>. 
            Returns corresponding integer value if valid, otherwise None is returned.
        """
        try:
            value = int(string)
            if value >= min and value <= max:
                return value, ""
        except:
            return None, "Given value is not a integer."
        return None, "Given value is not in a range  [{}, {}].".format(min, max)

    
    @staticmethod
    def validate_float(string, min = sys.float_info.min, max = sys.float_info.max):
        """
            Checks that given <string> is valid float and between <min> and <max>. 
            Returns corresponding float value if valid, otherwise None is returned.
        """
        try:
            value = float(string)
            if value >= min and value <= max:
                return value, ""
        except:
            return None, "Given value is not a floating point."
        return None, "Given value is not in a range [{}, {}].".format(min, max)

    
    @staticmethod
    def validate_folder(string):
        """
            Creates folder named <string> if not previously exist. Returns absolute
            value to folder if no errors occur, otherwise returns None.
        """
        try:
            Path(string).mkdir(parents=True, exist_ok=True)
            return Path(string).resolve(), ""
        except:
            pass
        return None, "Cannot create folder named {}.".format(string)
    


class SimulationParameter:
    """
        Class for single parameter used in simulator. Contains default value, validator and additional args for validator.
    """
    def __init__(self, description, default, validator, *args):
        self.__validator = validator
        self.__description = description
        self.__default_value = default
        self.__args = args


    def get_default_value(self):
        """
            Returns default value.
        """
        return self.__default_value


    def get_description(self):
        """
            Returns parameter desrciption.
        """
        return self.__description


    def validate(self, string):
        """
            Validates provided <string> against validator.
        """
        return self.__validator(string, *self.__args)

    

class SimulationParameters():

  
    def __init__(self, lines, supported_parameters):
        """
            Parses parameters from <lines>, where each line is format <PARAMATER_NAME>: <PARAMETER_VALUE>.
        """

        # Fill with defaults:
        self._parameters = {k:v.get_default_value() for k, v in supported_parameters.items()}

        # Override default values with provided values:
        for i in range(len(lines)):

            name, value = self._split_param_line(lines[i])

            # Validate syntax:
            if name is None:
                if not self._is_empty_or_comment_line(lines[i]):
                    raise SimulationParameterException("Wrong syntax at line {}.".format(i+1))
                continue
            elif not name in supported_parameters:
                raise SimulationParameterException("Unknown parameter '{}' at line {}.".format(name, i+1))

            # Parse:
            parsed, error = supported_parameters[name].validate(value)

            # Validate parsing:
            if parsed is None:
                raise SimulationParameterException("Parameter '{}' has non-valid value at the line {}.\n{}".format(name, i+1, error))

            self._parameters[name] = parsed
        

    def __getitem__(self, p):
        """
            Returns value of the parameter named <p>.
        """
        return self._parameters[p]


    def _split_param_line(self, line):
        """ 
            Splits line according to syntax: <KEY>: <VALUE>. Ignores empty lines and single 
            line comments that start with '#' character.
        """
        found = re.search(r"(^[^\s]+):\s*([^\s]+)\s*[\n|\#]", line)
        if found is not None and len(found.groups()) == 2:
            return found.groups()[0], found.groups()[1]
        return None, None


    def _is_empty_or_comment_line(self, line):
        """
            Checks if line is empty or line is commented.
        """
        return bool(re.search(r"^\s*(\#.*)|(^\n)", line))

