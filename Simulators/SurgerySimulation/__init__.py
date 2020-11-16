from Simulators.SimulatorBase import SimulatorBase
from Core.Parameters import SimulationParameter, validate_integer, validate_float, validate_enum
from Logging.Logging import Logger, LogLevel
from enum import Enum
import simpy
import argparse
import sys

class PatientStatus(Enum):
    WAITING = 0,
    PREPARED = 1,
    OPERATED = 2,
    RECOVERED = 4

class PatientRecord:

    def __init__(self):
        self.status = PatientStatus.WAITING
        # Time of arrival

class Patient:
    """
        TODO: id, toa, condition, etc..
    """
    pass


class PatientGenerator:
    """
        TODO: use parameters to generate..
    """
    def __init__(self):
        pass



    def _generate_new_patient(self):
        pass


class PreparationPlaces: # Facility:
    pass


class OperationPlaces: # Facility:
    pass



class SurgerySimulator(SimulatorBase):
    """
        Simulation scenario for TIES481 course surgery case.
    """

    def __init__(self):
        
        # TODO: Parse supported parameters from the file
        super().__init__({ "number-of-recovery-places":  SimulationParameter(10, validate_integer, 1, 300),
                           "number-of-operation-places": SimulationParameter(10, validate_integer, 1, 100),
                           "severe-patient-portion":     SimulationParameter(0.5, validate_float, 0, 1.0)
                         });



        # Print custom error message if correct path is not provided:
        try:
            conf_file = self._parse_command_line_arguments()
        except:
            print("Please provide correct path to file containing simulation configuration by '--conf' command line option")
            sys.exit()

        
        # Parse arguments for simulation:
        self.create(conf_file.conf.readlines())
        # TODO: close file in case of exception
        conf_file.conf.close()

        Logger.log(LogLevel.INFO, "Start creating simulation with configuration from file: " + str(sys.argv[-1]))

        # TODO: Initialize simulator with parameters:




    def _parse_command_line_arguments(self):
        """
            Parses command line arguments.
        """
        parser = argparse.ArgumentParser(description='Simulation configuration are provided by single file.')
        parser.add_argument('--conf', 
                            type=argparse.FileType('r'), 
                            default=sys.stdin,
                            help='File containing parameters used in simulator.')
        return parser.parse_args()




