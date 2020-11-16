from Simulators.SimulatorBase import SimulatorBase
from Core.Parameters import SimulationParameter, validate_integer, validate_float, validate_enum
from Logging.Logging import Logger, LogLevel 
import simpy
import argparse
import sys

class Patient:
    """
        TODO: id, toa, condition, etc..
    """
    pass


class PatientGenerator:
    """
        TODO: use parameters to generate..
    """
    pass


class SurgerySimulator(SimulatorBase):
    """
        Simulation scenario for TIES481 course surgery case.
    """

    def __init__(self):
        
        # TODO: Split into common and simulation specific parameters
        super().__init__({ "log-level":                  SimulationParameter("INFO", validate_enum, LogLevel),
                           "random-seed":                SimulationParameter(1, validate_integer, 0),
                           "number-of-recovery-places":  SimulationParameter(10, validate_integer, 1, 300),
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




