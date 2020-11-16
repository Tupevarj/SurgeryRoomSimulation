from Simulations.SimulationBase import SimulationBase
from Simulations.SurgerySimulation.Patients import PatientGenerator
from Simulations.SurgerySimulation.Phases import RecoveryPlaces, OperationPlaces, PreparationPlaces
from Core.Parameters import SimulationParameter, ParameterValidation as PV
from Statistics.Statistics import StatisticsCollection, ScalarStatistic
from Logging.Logging import Logger, LogLevel
import simpy
import argparse
import sys


class SurgerySimulator(SimulationBase):
    """
        Simulation scenario for TIES481 course surgery case.
    """

    def __init__(self):
        
        super().__init__({ "number-of-preparation-places":  SimulationParameter(10, PV.validate_integer, 1, 300),
                           "number-of-operation-places":    SimulationParameter(10, PV.validate_integer, 1, 100),
                           "severe-patient-portion":        SimulationParameter(0.5, PV.validate_float, 0, 1.0),
                           "patient-interval":              SimulationParameter(1.0, PV.validate_float, 0.0),
                           "preparation-time-severe":       SimulationParameter(1.0, PV.validate_float, 0.0),
                           "preparation-time-mild":         SimulationParameter(0.5, PV.validate_float, 0.0),
                           "operation-time-severe":         SimulationParameter(5.5, PV.validate_float, 0.0),
                           "operation-time-mild":           SimulationParameter(2.5, PV.validate_float, 0.0),
                           "recovery-time-severe":          SimulationParameter(48.0, PV.validate_float, 0.0),
                           "recovery-time-mild":            SimulationParameter(12.0, PV.validate_float, 0.0),
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

        Logger.log(LogLevel.INFO, "Prepared simulation with configuration from file: " + str(sys.argv[-1]))

        # Created instances with provided parameters:
        recovery    = RecoveryPlaces(None)
        operation   = OperationPlaces(self.create_resource(self.parameters["number-of-operation-places"]), recovery)
        preparation = PreparationPlaces(self.create_resource(self.parameters["number-of-preparation-places"]), operation)

        # Create patient generator:
        patient_generator = PatientGenerator(self.parameters["patient-interval"], self.parameters["severe-patient-portion"])

        StatisticsCollection.add_statistic(ScalarStatistic(), "test")
        StatisticsCollection.update_statistic("test")

        # Start simulation (with entry point at patient generator):
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




