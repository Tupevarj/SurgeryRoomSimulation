from Core.SimulationBase import SimulationBase
from SimulationScenarios.Patients import PatientGenerator, PatientRecords, PatientStatus
from SimulationScenarios.Phases import RecoveryUnits, OperationUnits, PreparationUnits
from Core.Parameters import SimulationParameter, ParameterValidation as PV
from Statistics.Statistics import StatisticsCollection, ScalarStatistic, StatisticsWriterStdout, TableStatistic, StatisticsWriterFile
from Logging.Logging import SimLogger as Logger, LogLevel
from Statistics.Statistics import *
from pathlib import Path
import simpy
import argparse
import sys

"""


"""

class SimulationScenarioSurgery(SimulationBase):
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

        self._statistics = {
                            "scalars.txt":
                              {
                                  "number_of_prepared":      CounterStatistic("Number of patients PREPARED in total"),
                                  "number_of_operated":      CounterStatistic("Number of patients OPERATED in total"),
                                  "number_of_recovered":     CounterStatistic("Number of patients RECOVERED in total"),
                                  "mean_time_per_prepare":   ScalarMeanStatistic("Mean time spent from WAITING to PREPARED", "hours"),
                                  "mean_time_per_operate":   ScalarMeanStatistic("Mean time spent from PREPARED to OPERATED", "hours"),
                                  "mean_time_per_patient":   ScalarMeanStatistic("Mean time spent from WAITING to RECOVERED", "hours"),
                                  "usage_of_operation_unit": TableStatistic(["Time", "Reserved", "Total"], self.calculate_utilization),
                              },
                            "entrance-queue.csv":
                              {
                                  "length_entrance_queue":   TableStatistic(["Time", "Entrance queue length"]),
                              },
                            }

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

        # Enable statistics:
        [StatisticsCollection.add_statistic(stat[1], stat[0]) for group in self._statistics.keys() for stat in self._statistics[group].items()]
        
        print("-" * 150)
        Logger.log(LogLevel.INFO, "Prepared simulation with configuration from file: " + str(sys.argv[-1]) + ".")

        # Created instances with provided parameters:
        self._recovery = RecoveryUnits(self.create_resource(self.parameters["number-of-recovery-units"]), 
                                  self.parameters["recovery-time-mild"], 
                                  self.parameters["recovery-time-severe"])
        self._operation = OperationUnits(self.create_resource(self.parameters["number-of-operation-units"]), 
                                    self._recovery, 
                                    self.parameters["operation-time-mild"], 
                                    self.parameters["operation-time-severe"])
        self._preparation = PreparationUnits(self.create_resource(self.parameters["number-of-preparation-units"]), 
                                        self._operation, 
                                        self.parameters["preparation-time-mild"], 
                                        self.parameters["preparation-time-severe"])

        # Create records:
        patient_records = PatientRecords(self.on_patient_status_changed)

        self._waiting_list = []

        # Create patient generator:
        patient_generator = PatientGenerator(self.parameters["patient-interval"], self.parameters["severe-patient-portion"], patient_records)
        
        # Start simulation (with entry point at patient generator):
        Logger.log(LogLevel.INFO, "Starting simulation.")
        self.run(patient_generator.run, self._preparation.enter_phase)
        Logger.log(LogLevel.INFO, "Simulation ended successfully.")

        # Write all statistics to files:
        output = StatisticsWriterFile()
        [StatisticsCollection.output_statistic(self._statistics[file].keys(), output, self.parameters["result-folder"] / file) for file in self._statistics.keys()]

        # Write scalar statistics to stdout:
        print("-" * 150)
        output = StatisticsWriterStdout()
        [StatisticsCollection.output_statistic(stat, output) for stat in self._statistics["scalars.txt"].keys()]
            

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


    def on_patient_status_changed(self, status, patient, time_stamp):
        """
            Callback to collect statistics when patient status is changed.
        """

        StatisticsCollection.update_statistic("length_entrance_queue",   [time_stamp, len(self._waiting_list)])
        StatisticsCollection.update_statistic("usage_of_operation_unit", [time_stamp, self._operation.resources.count, self._operation.resources.capacity])

        if status == PatientStatus.WAITING:
            self._waiting_list.append(patient)
        elif status == PatientStatus.IN_PREPARATION:
            self._waiting_list.remove(patient)
        elif status == PatientStatus.PREPARED:
            StatisticsCollection.update_statistic("mean_time_per_prepare", patient.time_stamps[status] - patient.time_stamps[PatientStatus.WAITING])
            StatisticsCollection.update_statistic("number_of_prepared")
        elif status == PatientStatus.OPERATED:
            StatisticsCollection.update_statistic("mean_time_per_operate", patient.time_stamps[status] - patient.time_stamps[PatientStatus.PREPARED])
            StatisticsCollection.update_statistic("number_of_operated")
        elif status == PatientStatus.RECOVERED:
            StatisticsCollection.update_statistic("mean_time_per_patient", patient.time_stamps[status] - patient.time_stamps[PatientStatus.WAITING])
            StatisticsCollection.update_statistic("number_of_recovered")


    def calculate_utilization(self, values):
        """
            Calculates the utilization of the operation theater. Passed as formatter to TableStatistic.
        """
        utilization = 0
        utilization_max = self.parameters["number-of-operation-units"] * self.parameters["simulation-time"]
       
        last_time_stamp = 0
        for i in range(0, len(values)):
            if last_time_stamp != values[i][0]:
                utilization += (values[i][0] - last_time_stamp) * values[i][1]
                last_time_stamp = values[i][0]

        return "{:80} {:.2f} %".format("Utilization of the operation theater ", utilization / utilization_max * 100.0)
