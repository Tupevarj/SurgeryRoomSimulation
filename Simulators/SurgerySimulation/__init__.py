from Simulators.SimulationBase import SimulationBase
from Core.Parameters import SimulationParameter, validate_integer, validate_float, validate_enum
from Simulators.SurgerySimulation.Patients import PatientGenerator
from Logging.Logging import Logger, LogLevel
from Simulators.SurgerySimulation.Phases import *
import simpy
import argparse
import sys


class SurgerySimulator(SimulationBase):
    """
        Simulation scenario for TIES481 course surgery case.
    """

    def __init__(self):
        
        super().__init__({ "number-of-recovery-places":  SimulationParameter(10, validate_integer, 1, 300),
                           "number-of-operation-places": SimulationParameter(10, validate_integer, 1, 100),
                           "severe-patient-portion":     SimulationParameter(0.5, validate_float, 0, 1.0),
                           "patient-interval":           SimulationParameter(1.0, validate_float, 0.0),
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

        # TODO: Created instances with provided parameters:
        recovery    = RecoveryPlaces(self.create_resource(self.parameters["number-of-recovery-places"]), None)
        operation   = OperationPlaces(self.create_resource(self.parameters["number-of-operation-places"]), recovery)
        preparation = PreparationPlaces(operation)

        # Create queue:
        #self.operationsss = simpy.Resource(env, capacity=2)

        patient_generator = PatientGenerator(self.parameters["patient-interval"], self.parameters["severe-patient-portion"])
        
        #self.register_process(patient_generator.run, preparation.enter_phase)
        #self.add_process(preparation.run)

        # Start simulation (with entry point patient generator):
        self.run(patient_generator.run, preparation.enter_phase)


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




