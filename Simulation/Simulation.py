from Core.Parameters.Parameters import SimulationParameter, SimulationParameters, ParameterValidation as PV
from Simulation.Patients import PatientGenerator, PatientRecords, PatientStatus, PatientCondition
from Simulation.Phases import RecoveryUnits, OperationUnits, PreparationUnits
from Core.Logging.Logging import SimLogger as Logger, LogLevel
from Core.Distributions import RandomGenerator as Random
from Core.Distributions import Distribution, Rng
from Core.Statistics.Statistics import *
from pathlib import Path
from enum import IntEnum
import argparse
import simpy
import sys

"""


"""

class LogOutput(IntEnum):
    """
        Enum to simplify setting of logging output parameter.
        (Not used by logging module).
    """
    LOG_NONE      = 0
    LOG_TO_STDOUT = 2
    LOG_TO_FILE   = 4
    LOG_BOTH      = 8


class Simulation():
    """
        Simulation scenario for TIES481 course surgery case.

    """
    __supported_parameters = {
            "log-level":                   SimulationParameter("Log level: DEBUG, INFO, WARNING, ERROR or CRITICAL.", "INFO", PV.validate_enum, LogLevel),
            "log-out":                     SimulationParameter("Log output: LOG_NONE, LOG_TO_STDOUT, LOG_TO_FILE or LOG_BOTH. LOG_BOTH will output log into stdout and file both.", "LOG_BOTH", PV.validate_enum, LogOutput),
            "sample-warm-up":              SimulationParameter("Time in hours before first sample is taken.", 1000, PV.validate_integer, 0),
            "sample-interval":             SimulationParameter("Timeout in hours between single samples.", 1000, PV.validate_integer, 0),
            "sample-time":                 SimulationParameter("Length of single sample in hours.", 1000, PV.validate_integer, 0),
            "sample-count":                SimulationParameter("Number of samples int total.", 20, PV.validate_integer, 0),
            "random-seed":                 SimulationParameter("Start seed for random number generator.", 1, PV.validate_integer, 0),
            "result-folder":               SimulationParameter("Folder to store simulation results.", "./", PV.validate_folder),
            "number-of-preparation-units": SimulationParameter("Number of preparation units [1 - 100].", 10, PV.validate_integer, 1, 100),
            "number-of-operation-units":   SimulationParameter("Number of operation units [1 - 100].", 4, PV.validate_integer, 1, 100),
            "number-of-recovery-units":    SimulationParameter("Number of operation units [1 - 100].", 10, PV.validate_integer, 1, 100),
            "patient-interval":            SimulationParameter("Patient arrival rate in hours. Format: [\"EXPONENTIAL\", <mean>] or [\"UNIFORM\", <min>, <max>].", ["EXPONENTIAL", 25.0], PV.validate_object, Rng),
            "number-of-runs":              SimulationParameter("Number of simulations runs with different random seed, starting from <random-seed> and inceased by one between runs.", 1, PV.validate_integer, 0),
            "base-preparation-time":       SimulationParameter("Base time (no additional multipliers) in hours that preparation takes. Format: [\"EXPONENTIAL\", <mean>] or [\"UNIFORM\", <min>, <max>].", ["EXPONENTIAL", 20.0], PV.validate_object, Rng),
            "base-operation-time":         SimulationParameter("Base time (no additional multipliers) in hours that operation takes. Format: [\"EXPONENTIAL\", <mean>] or [\"UNIFORM\", <min>, <max>]. ", ["EXPONENTIAL", 40.0], PV.validate_object, Rng),
            "base-recovery-time":          SimulationParameter("Base time (no additional multipliers) in hours that recovery takes. Format: [\"EXPONENTIAL\", <mean>] or [\"UNIFORM\", <min>, <max>].", ["EXPONENTIAL", 40.0], PV.validate_object, Rng),
            "patient-condition-*":         SimulationParameter("Different condition for patients. Array of:\n -priority (lower priorities are more urgent),\n -generator portion (0 => 0%, 1.0 => 100%),\n -mean death rate per 100 hours elapsed before OPERATED (0 => 0%, 1.0 => 100%)\n -array of 3 different service time multipliers (preparation, operation, recovery).\n", 
                                                               PatientCondition("[1, 1.0, 0.0, [1.0, 1.0, 1.0]]"), PV.validate_object, PatientCondition),
        }

    __statistics = {
            "number_of_prepared":         SampleCollection(desc_l="Number of patients PREPARED in total",         desc_s="total_prepared",       type=Counter),
            "number_of_operated":         SampleCollection(desc_l="Number of patients OPERATED in total",         desc_s="total_operated",       type=Counter),
            "number_of_recovered":        SampleCollection(desc_l="Number of patients RECOVERED in total",        desc_s="total_recoved",        type=Counter),
            "number_of_deceased":         SampleCollection(desc_l="Number of patients DECEASED in total",         desc_s="total_deceased",       type=Counter),
            "total-number-of-patients":   SampleCollection(desc_l="Total number of patients generated.",          desc_s="total_patients",       type=Counter),
            "patient-generator-interval": SampleCollection(desc_l="True interval of generating patients",         desc_s="interval_patients",    unit="hours"),
            "mean_time_per_prepare":      SampleCollection(desc_l="Mean time spent from WAITING to PREPARED",     desc_s="from_wait_to_prep",    unit="hours"),
            "mean_time_per_operate":      SampleCollection(desc_l="Mean time spent from PREPARED to OPERATED",    desc_s="from_prep_to_oper",    unit="hours"),
            "mean_time_per_patient":      SampleCollection(desc_l="Mean time spent from WAITING to RECOVERED",    desc_s="from_wait_to_reco",    unit="hours"),
            "mean-in-preparation-time":   SampleCollection(desc_l="Mean preparation time based on distribution.", desc_s="mean_prep_time_distr", unit="hours"),
            "mean-in-operation-time":     SampleCollection(desc_l="Mean operation time based on distribution.",   desc_s="mean_oper_time_distr", unit="hours"),
            "mean-in-recovery-time":      SampleCollection(desc_l="Mean recovery time based on distribution.",    desc_s="mean_oper_reco_distr", unit="hours"),
            "usage_of_operation_unit":    SampleCollection(desc_l="Utilization of the operation theater",         desc_s="operation_usage",      unit="%"),
            "arrival-queue-length":       SampleCollection(desc_l="Patients at the arrival queue",                desc_s="arr_queue_length"),
            "idle-capacity-preparation":  SampleCollection(desc_l="Idle capacity at prepration",                  desc_s="idle_capacity"),
            "rate-blocking-operations":   SampleCollection(desc_l="Moving to recovery blocked",                   desc_s="move_reco_blocked",    unit="%"),
            "all-recovery-units-busy":    SampleCollection(desc_l="All recovery units are busy",                  desc_s="all_reco_busy",        unit="%"),
        }

    def __init__(self):

        # Print custom error message if correct path is not provided:
        try:
            command_line_args = self.__parse_command_line_arguments()
        except:
            print("Please provide correct path to file containing simulation configuration by '--conf' command line option or use --params command line option to print all supported parameters.")
            sys.exit()

        if command_line_args.params:
            print("\n".join(["{:30} {} Defaults to: {}.".format(param[0], param[1].get_description().replace("\n", "\n" + " "*30), param[1].get_default_value()) for param in self.__supported_parameters.items()]))
            return

        # Parse parameters for the simulation:
        self.__parameters = SimulationParameters(command_line_args.conf.readlines(), self.__supported_parameters)
        # TODO: close file in case of exception
        command_line_args.conf.close()

        
        # Remove default value from patient-types if user provided types exists, otherwise name * to DEFAULT:
        self.__patient_types = self.__parameters["patient-condition-*"]
        if len(self.__patient_types) > 1:
            del self.__patient_types["*"]
        else:
            self.__patient_types["DEFAULT"] = self.__patient_types.pop("*")
            
        self.__environment = simpy.Environment()
        
        # Initialize logger with requested log level and log all used parameters:
        Logger(self.__parameters["log-level"], self.__environment, stdout=self.__parameters["log-out"] & 10, file = self.__parameters["result-folder"] / "log.log" if self.__parameters["log-out"] & 12 else None)
        Logger.log(LogLevel.INFO, "Prepared simulation with configuration from file: " + str(sys.argv[-1]) + ".")
        Logger.log(LogLevel.INFO, "Starting simulation with following parameters:\n" +  "\n".join(["{:30} {}".format(p, self.__parameters[p]) for p in self.__supported_parameters]))
        

        # Initialize statistics:
        self.__statistics = { **{ "patient-portion-" + k: SampleCollection(desc_l="True portion of {} patients".format(k), desc_s="portion_{}".format(k), unit="%") for k in self.__patient_types.keys()},  **self.__statistics }
        Statistics()
        [Statistics.add_statistic(name, stat) for name, stat in self.__statistics.items()]

        Logger.log(LogLevel.INFO, "Starting simulation.")
        
        for r in range(0, self.__parameters["number-of-runs"]):
            
            print("-" * 150)
            Logger.log(LogLevel.INFO, "Starting simulation run {}.".format(r))
        
            # Initialize RNG:
            Random(self.__parameters["random-seed"] + r)
            
            # Created instances with provided parameters:
            self.__recovery =    RecoveryUnits(simpy.PriorityResource(self.__environment, capacity=self.__parameters["number-of-recovery-units"]))
            self.__operation =   OperationUnits(simpy.PriorityResource(self.__environment, capacity=self.__parameters["number-of-operation-units"]), self.__recovery)
            self.__preparation = PreparationUnits(simpy.PriorityResource(self.__environment, capacity=self.__parameters["number-of-preparation-units"]), self.__operation)

            # Create records:
            patient_records = PatientRecords(self.on_patient_status_changed)

            # List to count patients at arrival queue:
            self.__arrival_queue = []
        
            # Create patient generator:
            patient_generator = PatientGenerator(self.__parameters["patient-interval"].initialize(), patient_records, {
                                                     PatientStatus.IN_PREPARATION: self.__parameters["base-preparation-time"].initialize(),
                                                     PatientStatus.IN_OPERATION:   self.__parameters["base-operation-time"].initialize(),
                                                     PatientStatus.IN_RECOVERY:    self.__parameters["base-recovery-time"].initialize()
                                                  }, self.__patient_types)
                                              
            # Add monitor process:
            self.__environment.process(self.__sampler())

            # Start simulation (with entry point at patient generator):
            self.__environment.process(patient_generator.run(self.__environment, self.__preparation.enter_phase))

            # Calculate total simulation time:
            simulation_time = self.__parameters["sample-warm-up"] + self.__parameters["sample-count"] * (self.__parameters["sample-interval"] + self.__parameters["sample-time"]) - self.__parameters["sample-interval"]

            self.__environment.run(until=simulation_time)

            # Rest environment:
            self.__environment = simpy.Environment()


        Logger.log(LogLevel.INFO, "Simulation ended successfully.")
        
        # Output last five statistics to stdout:
        print("{}\n{}\n{}".format("-" * 150, Statistics.get_as_string(list(self.__statistics.keys())[-5:]), "-" * 150))

        with (self.__parameters["result-folder"] / "statistics.csv").open('w') as file:
            file.write(Statistics.get_as_csv(self.__statistics.keys()) + "\n")



    def __sampler(self):
        """
            Sampler method takes care of sampling with specific interval and length.
            Also writes statistics with resolution to 1 time unit.
        """

        Logger.log(LogLevel.INFO, "Starting simulation warm-up period.")
        yield self.__environment.timeout(self.__parameters["sample-warm-up"])
        Logger.log(LogLevel.INFO, "Warm-up period ended, start taking samples.")

        while True:
            Statistics.start_sample()
            Logger.log(LogLevel.INFO, "Start taking new sample.")

            for t in range(self.__parameters["sample-time"]):
                yield self.__environment.timeout(1)
                Statistics.update_sample("usage_of_operation_unit",   self.__operation.resources.count / self.__operation.resources.capacity * 100.0)
                Statistics.update_sample("arrival-queue-length",      len(self.__arrival_queue))
                Statistics.update_sample("idle-capacity-preparation", self.__preparation.resources.capacity - self.__preparation.resources.count)
                Statistics.update_sample("all-recovery-units-busy",   100.0 if self.__recovery.resources.capacity == self.__recovery.resources.count else 0)
            
            Statistics.end_sample()
            Logger.log(LogLevel.INFO, "Sample taken.")

            # Output statistics to stdout for current sample:
            print("{}\n{}\n{}".format("-" * 150, Statistics.get_as_string(self.__statistics.keys(), -1), "-" * 150))

            # Wait until time to get next sample:
            yield self.__environment.timeout(self.__parameters["sample-interval"])




    def __parse_command_line_arguments(self):
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

        if status == PatientStatus.WAITING:
            self.__arrival_queue.append(patient)
        elif status == PatientStatus.IN_PREPARATION:
            self.__arrival_queue.remove(patient)
        elif status == PatientStatus.PREPARED:
            Statistics.update_sample("number_of_prepared")
        elif status == PatientStatus.OPERATED:
            Statistics.update_sample("number_of_operated")
            #StatisticsCollection.update_statistic("rate-blocking-operations", [time_stamp,  1 if self.__recovery.resources.capacity == self.__recovery.resources.count  else 0])
            Statistics.update_sample("rate-blocking-operations", 100.0 if self.__recovery.resources.capacity == self.__recovery.resources.count  else 0)
        elif status == PatientStatus.RECOVERED:
            Statistics.update_sample("mean_time_per_prepare", patient.time_stamps[PatientStatus.PREPARED] - patient.time_stamps[PatientStatus.WAITING])
            Statistics.update_sample("mean_time_per_operate", patient.time_stamps[PatientStatus.OPERATED] - patient.time_stamps[PatientStatus.PREPARED])
            Statistics.update_sample("mean_time_per_patient", patient.time_stamps[PatientStatus.RECOVERED] - patient.time_stamps[PatientStatus.WAITING])
            Statistics.update_sample("number_of_recovered")
        elif status == PatientStatus.DECEASED:
            Statistics.update_sample("number_of_deceased")

