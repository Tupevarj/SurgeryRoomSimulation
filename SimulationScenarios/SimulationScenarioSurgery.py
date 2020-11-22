from Core.SimulationBase import SimulationBase
from SimulationScenarios.Patients import PatientGenerator, PatientRecords, PatientStatus, PatientCondition
from SimulationScenarios.Phases import RecoveryUnits, OperationUnits, PreparationUnits
from Core.Parameters import SimulationParameter, ParameterValidation as PV
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
                           "patient-interval":              SimulationParameter("Patient arrival interval in hours.", 1.0, PV.validate_float, 0.0),
                           "base-preparation-time":         SimulationParameter("Mean base time (no additional multipliers) in hours that patient preparation takes.", 20.0, PV.validate_float, 0.0),
                           "base-operation-time":           SimulationParameter("Mean base time (no additional multipliers) in hours that operation takes.", 40.0, PV.validate_float, 0.0),
                           "base-recovery-time":            SimulationParameter("Mean base time (no additional multipliers) in hours that recovery takes.", 40.0, PV.validate_float, 0.0),
                           "patient-condition-*":           SimulationParameter("Different condition for patients. Array of:\n -priority (lower priorities are more urgent),\n -generator portion (0 => 0%, 1.0 => 100%),\n -mean death rate per 100 hours elapsed before OPERATED (0 => 0%, 1.0 => 100%)\n -array of 3 different service time multipliers (preparation, operation, recovery).\n", 
                                                                                PatientCondition("[1, 1.0, 0.0, [1.0, 1.0, 1.0]]"), PV.validate_object, PatientCondition)
                         });

        self._statistics = {
                            "scalars.txt":
                              {
                                  "number_of_prepared":      CounterStatistic("Number of patients PREPARED in total"),
                                  "number_of_operated":      CounterStatistic("Number of patients OPERATED in total"),
                                  "number_of_recovered":     CounterStatistic("Number of patients RECOVERED in total"),
                                  "number_of_deceased":      CounterStatistic("Number of patients DECEASED in total"),
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
        [StatisticsCollection.add_statistic(stat[0], stat[1]) for group in self._statistics.keys() for stat in self._statistics[group].items()]
        
        print("-" * 150)
        Logger.log(LogLevel.INFO, "Prepared simulation with configuration from file: " + str(sys.argv[-1]) + ".")

        # Created instances with provided parameters:
        self._recovery = RecoveryUnits(self.create_resource(self.parameters["number-of-recovery-units"]))
        self._operation = OperationUnits(self.create_resource(self.parameters["number-of-operation-units"]), self._recovery)
        self._preparation = PreparationUnits(self.create_resource(self.parameters["number-of-preparation-units"]), self._operation)

        # Create records:
        patient_records = PatientRecords(self.on_patient_status_changed)

        self._waiting_list = []
        
        # Remove default value from patient-types if user provided types exists, otherwise name * to DEFAULT:
        patient_types = self.parameters["patient-condition-*"]
        if len(patient_types) > 1:
            del patient_types["*"]
        else:
            patient_types["DEFAULT"] = patient_types.pop("*")

        # Create patient generator:
        patient_generator = PatientGenerator(self.parameters["patient-interval"], patient_records,
                                              {
                                                 PatientStatus.IN_PREPARATION: self.parameters["base-preparation-time"],
                                                 PatientStatus.IN_OPERATION: self.parameters["base-operation-time"],
                                                 PatientStatus.IN_RECOVERY: self.parameters["base-recovery-time"]
                                              }, patient_types)
                                              
        # Start simulation (with entry point at patient generator):
        Logger.log(LogLevel.INFO, "Starting simulation.")
        self.run(patient_generator.run, self._preparation.enter_phase)
        Logger.log(LogLevel.INFO, "Simulation ended successfully.")

        # Write all statistics to files:
        output = StatisticsWriterFile()
        [StatisticsCollection.output_statistic(self._statistics[file].keys(), output, self.parameters["result-folder"] / file) for file in self._statistics.keys()]
        patient_generator.output_statistics(output, self.parameters["result-folder"] / "scalars-generator.txt")

        # Write scalar statistics to stdout:
        print("-" * 150)
        output = StatisticsWriterStdout()
        [StatisticsCollection.output_statistic(stat, output) for stat in self._statistics["scalars.txt"].keys()]
        patient_generator.output_statistics(output)
            

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
            StatisticsCollection.update_statistic("number_of_prepared")
        elif status == PatientStatus.OPERATED:
            StatisticsCollection.update_statistic("number_of_operated")
        elif status == PatientStatus.RECOVERED:
            StatisticsCollection.update_statistic("mean_time_per_prepare", patient.time_stamps[PatientStatus.PREPARED] - patient.time_stamps[PatientStatus.WAITING])
            StatisticsCollection.update_statistic("mean_time_per_operate", patient.time_stamps[PatientStatus.OPERATED] - patient.time_stamps[PatientStatus.PREPARED])
            StatisticsCollection.update_statistic("mean_time_per_patient", patient.time_stamps[PatientStatus.RECOVERED] - patient.time_stamps[PatientStatus.WAITING])
            StatisticsCollection.update_statistic("number_of_recovered")
        elif status == PatientStatus.DECEASED:
            StatisticsCollection.update_statistic("number_of_deceased")


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
