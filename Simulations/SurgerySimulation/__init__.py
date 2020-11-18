from Simulations.SimulationBase import SimulationBase
from Simulations.SurgerySimulation.Patients import PatientGenerator, PatientRecords
from Simulations.SurgerySimulation.Phases import RecoveryUnits, OperationUnits, PreparationUnits
from Core.Parameters import SimulationParameter, ParameterValidation as PV
from Statistics.Statistics import StatisticsCollection, ScalarStatistic, StatisticsOutConsole
from Logging.Logging import SimLogger as Logger, LogLevel
import simpy
import argparse
import sys


class SurgerySimulation(SimulationBase):
    """
        Simulation scenario for TIES481 course surgery case.
    """

    def __init__(self):
        
        super().__init__({ "number-of-preparation-units":   SimulationParameter("Number of preparation units [1 - 100].", 10, PV.validate_integer, 1, 100),
                           "number-of-operation-units":     SimulationParameter("Number of operation units [1 - 100].", 4, PV.validate_integer, 1, 100),
                           "number-of-recovery-units":      SimulationParameter("Number of operation units [1 - 100].", 10, PV.validate_integer, 1, 100),
                           "severe-patient-portion":        SimulationParameter("Portion of severe patients (0 => 0%, 1.0 => 100%) [0 - 1.0].", 0.5, PV.validate_float, 0, 1.0),
                           "patient-interval":              SimulationParameter("Patient arrival interval in hours.", 1.0, PV.validate_float, 0.0),
                           "preparation-time-severe":       SimulationParameter("Time in hours that patient preparation takes for severe patients.", 1.0, PV.validate_float, 0.0),
                           "preparation-time-mild":         SimulationParameter("Time in hours that patient preparation takes for mild patients.", 0.5, PV.validate_float, 0.0),
                           "operation-time-severe":         SimulationParameter("Time in hours that operation takes for severe patients.", 5.5, PV.validate_float, 0.0),
                           "operation-time-mild":           SimulationParameter("Time in hours that operation takes for mild patients.", 2.5, PV.validate_float, 0.0),
                           "recovery-time-severe":          SimulationParameter("Time in hours that recovery takes for severe patients.", 48.0, PV.validate_float, 0.0),
                           "recovery-time-mild":            SimulationParameter("Time in hours that recovery takes for mild patients.", 12.0, PV.validate_float, 0.0),
                         });


        # Print custom error message if correct path is not provided:
        try:
            command_line_args = self._parse_command_line_arguments()
        except:
            print("Please provide correct path to file containing simulation configuration by '--conf' command line option")
            sys.exit()

        if command_line_args.params:
            self.print_supported_parameters()
            return
        
        # Parse arguments for simulation:
        self.create(command_line_args.conf.readlines())
        # TODO: close file in case of exception
        command_line_args.conf.close()
        
        print("-" * 150)
        Logger.log(LogLevel.INFO, "Prepared simulation with configuration from file: " + str(sys.argv[-1]) + ".")

        # Created instances with provided parameters:
        recovery = RecoveryUnits(self.create_resource(self.parameters["number-of-recovery-units"]), 
                                  self.parameters["recovery-time-mild"], 
                                  self.parameters["recovery-time-severe"])
        operation = OperationUnits(self.create_resource(self.parameters["number-of-operation-units"]), 
                                    recovery, 
                                    self.parameters["operation-time-mild"], 
                                    self.parameters["operation-time-severe"])
        preparation = PreparationUnits(self.create_resource(self.parameters["number-of-preparation-units"]), 
                                        operation, 
                                        self.parameters["preparation-time-mild"], 
                                        self.parameters["preparation-time-severe"])

        # Create records (TODO: Should be able to disable unwanted statistics):
        patient_records = PatientRecords()
        
        # Create patient generator:
        patient_generator = PatientGenerator(self.parameters["patient-interval"], self.parameters["severe-patient-portion"], patient_records)
        
        # Start simulation (with entry point at patient generator):
        Logger.log(LogLevel.INFO, "Starting simulation.")
        self.run(patient_generator.run, preparation.enter_phase)
        Logger.log(LogLevel.INFO, "Simulation ended successfully.")

        # Output statistics:
        print("-" * 150)
        PatientRecords.output_statistics(StatisticsOutConsole())


    def _parse_command_line_arguments(self):
        """
            Parses command line arguments.
        """
        parser = argparse.ArgumentParser(description='Simulation configuration are provided by single file.')
        parser.add_argument('--conf', 
                            type=argparse.FileType('r'), 
                            default=sys.stdin,
                            help='File containing parameters used in simulator.')
        parser.add_argument('--params', 
                            help='Print supported parameters.', action='store_true')
        return parser.parse_args()




