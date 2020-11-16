from Core.SimulationBase import SimulationBase
from Core.Parameters import SimulationParameter, validate_integer, validate_float
from Logging import LogLevel
import simpy
import argparse
import sys

class Patient:
    pass



class Simulation(SimulationBase):
    """
        Simulation scenario for TIES481 course surgery case.
    """

    def __init__(self):
        
        super().__init__({ "random-seed":                SimulationParameter(1, validate_integer, 0),
                           "number-of-recovery-places":  SimulationParameter(10, validate_integer, 1, 300),
                           "number-of-operation-places": SimulationParameter(10, validate_integer, 1, 100),
                           "severe-patient-portion":     SimulationParameter(0.5, validate_float, 0, 1.0)
                         });



        # Print custom error message if correct path is not provided:
        try:
            conf_file = self._parse_arguments()
        except:
            print("Please provide correct path to file containing simulation configuration by '--conf' command line option")
            sys.exit()

        self.LOGGER.log(LogLevel.INFO, "Start creating simulation with configuration from file: " + str(sys.argv[-1]))
        
        # Parse arguments for simulation:
        self.create(conf_file.conf.readlines())
        # TODO: close file in case of exception
        conf_file.conf.close()

        # TODO: Initialize simulator with parameters:




    def _parse_arguments(self):
        """
            Parses command line arguments.
        """
        parser = argparse.ArgumentParser(description='Simulation configuration are provided by single file.')
        parser.add_argument('--conf', 
                            type=argparse.FileType('r'), 
                            default=sys.stdin,
                            help='File containing parameters used in simulator.')
        return parser.parse_args()




