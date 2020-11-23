from Simulation.Patients import PatientGenerator, PatientRecords, PatientStatus, PatientCondition
from Simulation.Phases import RecoveryUnits, OperationUnits, PreparationUnits
from Core.Parameters.Parameters import SimulationParameter, SimulationParameters, ParameterValidation as PV
from Core.Distributions import RandomGenerator as Random
from Core.Logging.Logging import SimLogger as Logger, LogLevel
from Core.Statistics.Statistics import *
from enum import IntEnum
import simpy
from pathlib import Path
import simpy
import argparse
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
            "simulation-time":             SimulationParameter("Simulation time in hours.", 10, PV.validate_integer, 0),
            "random-seed":                 SimulationParameter("Start seed for random number generator.", 1, PV.validate_integer, 0),
            "result-folder":               SimulationParameter("Folder to store simulation results.", "./", PV.validate_folder),
            "number-of-preparation-units": SimulationParameter("Number of preparation units [1 - 100].", 10, PV.validate_integer, 1, 100),
            "number-of-operation-units":   SimulationParameter("Number of operation units [1 - 100].", 4, PV.validate_integer, 1, 100),
            "number-of-recovery-units":    SimulationParameter("Number of operation units [1 - 100].", 10, PV.validate_integer, 1, 100),
            "patient-interval":            SimulationParameter("Patient arrival interval in hours.", 1.0, PV.validate_float, 0.0),
            "number-of-runs":              SimulationParameter("Number of simulations runs with different random seed, starting from <random-seed> and inceased by one between runs.", 1, PV.validate_integer, 0),
            "base-preparation-time":       SimulationParameter("Mean base time (no additional multipliers) in hours that patient preparation takes.", 20.0, PV.validate_float, 0.0),
            "base-operation-time":         SimulationParameter("Mean base time (no additional multipliers) in hours that operation takes.", 40.0, PV.validate_float, 0.0),
            "base-recovery-time":          SimulationParameter("Mean base time (no additional multipliers) in hours that recovery takes.", 40.0, PV.validate_float, 0.0),
            "patient-condition-*":         SimulationParameter("Different condition for patients. Array of:\n -priority (lower priorities are more urgent),\n -generator portion (0 => 0%, 1.0 => 100%),\n -mean death rate per 100 hours elapsed before OPERATED (0 => 0%, 1.0 => 100%)\n -array of 3 different service time multipliers (preparation, operation, recovery).\n", 
                                                               PatientCondition("[1, 1.0, 0.0, [1.0, 1.0, 1.0]]"), PV.validate_object, PatientCondition),
        }

    
    __statistics = {
            "number_of_prepared":         StatisticScalar(SampleScalar, "Number of patients PREPARED in total", ""),
            "number_of_operated":         StatisticScalar(SampleScalar, "Number of patients OPERATED in total", ""),
            "number_of_recovered":        StatisticScalar(SampleScalar, "Number of patients RECOVERED in total", ""),
            "number_of_deceased":         StatisticScalar(SampleScalar, "Number of patients DECEASED in total", ""),
            "mean_time_per_prepare":      StatisticScalar(SampleScalarMean, "Mean time spent from WAITING to PREPARED", "hours"),
            "mean_time_per_operate":      StatisticScalar(SampleScalarMean, "Mean time spent from PREPARED to OPERATED", "hours"),
            "mean_time_per_patient":      StatisticScalar(SampleScalarMean, "Mean time spent from WAITING to RECOVERED", "hours"),
            "usage_of_operation_unit":    StatisticTable(SampleTable, [["Time", "h"], ["Usage", "%"]], "Utilization of the operation theater"),
            "arrival-queue-length":       StatisticTable(SampleTable, [["Time", "h"], "Queue length"], "Patients at the arrival queue"),
            "idle-capacity-preparation":  StatisticTable(SampleTable, [["Time", "h"], "Idle capacity"], "Idle capacity at prepration"),
            "rate-blocking-operations":   StatisticTable(SampleTable, [["Time", "h"], ["Blocking", "%"]], "Moving to recovery blocked"),
            "all-recovery-units-busy":    StatisticTable(SampleTable, [["Time", "h"], ["Busy", "%"]], "All recovery units are busy"),
            "length_entrance_queue":      StatisticTable(SampleTable, ["Time", "Entrance queue length"]),
            "patient-generator-interval": StatisticScalar(SampleScalarMean, "True interval of generating patients", "hours"),
            "mean-in-preparation-time":   StatisticScalar(SampleScalarMean, "Mean preparation time based on exponential distribution.", "hours"),
            "mean-in-operation-time":     StatisticScalar(SampleScalarMean, "Mean operation time based on exponential distribution.", "hours"),
            "mean-in-recovery-time":      StatisticScalar(SampleScalarMean, "Mean recovery time based on exponential distribution.", "hours"),
            "total-number-of-patients":   StatisticScalar(SampleScalar,     "Total number of patients generated.", ""),
            
        }



    def __init__(self):

        # Print custom error message if correct path is not provided:
        try:
            command_line_args = self._parse_command_line_arguments()
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
        patient_types = self.__parameters["patient-condition-*"]
        if len(patient_types) > 1:
            del patient_types["*"]
        else:
            patient_types["DEFAULT"] = patient_types.pop("*")
            
        self.__environment = simpy.Environment()
        
        # Initialize logger with requested log level and log all used parameters:
        Logger(self.__parameters["log-level"], self.__environment, stdout=self.__parameters["log-out"] & 10, file = self.__parameters["result-folder"] / "log.log" if self.__parameters["log-out"] & 12 else None)
        Logger.log(LogLevel.INFO, "Prepared simulation with configuration from file: " + str(sys.argv[-1]) + ".")
        Logger.log(LogLevel.INFO, "Starting simulation with following parameters:\n" +  "\n".join(["{:30} {}".format(p, self.__parameters[p]) for p in self.__supported_parameters]))
        

        # Initialize statistics:
        self.__statistics = { **{ "patient-portion-" + k: StatisticScalar(SampleScalarMean, "True portion of {} patients".format(k), "%") for k in patient_types.keys()},  **self.__statistics }
        Statistics()
        [Statistics.add_statistic(name, stat) for name, stat in self.__statistics.items()]

        Logger.log(LogLevel.INFO, "Starting simulation.")
        
        for r in range(0, self.__parameters["number-of-runs"]):
            
            print("-" * 150)
            Logger.log(LogLevel.INFO, "Starting simulation round {}.".format(r))
            # Initialize environment:
            self.__environment = simpy.Environment()
        
            # Initialize RNG:
            Random(self.__parameters["random-seed"] + r)
            
            # Add new samples to statistics:
            [Statistics.add_sample(name) for name in self.__statistics.keys()]
        
            # Created instances with provided parameters:
            self.__recovery = RecoveryUnits(simpy.PriorityResource(self.__environment, capacity=self.__parameters["number-of-recovery-units"]))
            self.__operation = OperationUnits(simpy.PriorityResource(self.__environment, capacity=self.__parameters["number-of-operation-units"]), self.__recovery)
            self.__preparation = PreparationUnits(simpy.PriorityResource(self.__environment, capacity=self.__parameters["number-of-preparation-units"]), self.__operation)

            # Create records:
            patient_records = PatientRecords(self.on_patient_status_changed)

            self._waiting_list = []
        
            # Create patient generator:
            patient_generator = PatientGenerator(self.__parameters["patient-interval"], patient_records, {
                                                     PatientStatus.IN_PREPARATION: self.__parameters["base-preparation-time"],
                                                     PatientStatus.IN_OPERATION:   self.__parameters["base-operation-time"],
                                                     PatientStatus.IN_RECOVERY:    self.__parameters["base-recovery-time"]
                                                  }, patient_types)
                                              
            # Add monitor process:
            self.__environment.process(self.__collect_statistics(self.__environment, 1))

            # Start simulation (with entry point at patient generator):
            self.__environment.process(patient_generator.run(self.__environment, self.__preparation.enter_phase))
            self.__environment.run(until=self.__parameters["simulation-time"])
            

            # Print statistics for current simulation round:
            print(self.__statistics["mean_time_per_prepare"].get_sample_as_str(r))
            print(self.__statistics["mean_time_per_operate"].get_sample_as_str(r))
            print(self.__statistics["mean_time_per_patient"].get_sample_as_str(r))
            print(self.__statistics["number_of_prepared"].get_sample_as_str(r))
            print(self.__statistics["number_of_operated"].get_sample_as_str(r))
            print(self.__statistics["number_of_recovered"].get_sample_as_str(r))
            print(self.__statistics["number_of_deceased"].get_sample_as_str(r))
            print(self.__statistics["arrival-queue-length"].get_sample_as_str(r, "Queue length"))
            print(self.__statistics["idle-capacity-preparation"].get_sample_as_str(r, "Idle capacity"))
            print(self.__statistics["rate-blocking-operations"].get_sample_as_str(r, "Blocking"))
            print(self.__statistics["all-recovery-units-busy"].get_sample_as_str(r, "Busy"))
            print(self.__statistics["patient-generator-interval"].get_sample_as_str(r))
            print(self.__statistics["total-number-of-patients"].get_sample_as_str(r))
            [print(self.__statistics[s].get_sample_as_str(r)) for s in ["patient-portion-" + k for k in patient_types.keys()]]
            



        Logger.log(LogLevel.INFO, "Simulation ended successfully.")
        print("-" * 150)

        # Print mean values based on invidual samples:
        print(self.__statistics["arrival-queue-length"].get_confidence_interval_as_str("Queue length"))
        print(self.__statistics["idle-capacity-preparation"].get_confidence_interval_as_str("Idle capacity"))
        print(self.__statistics["rate-blocking-operations"].get_confidence_interval_as_str("Blocking"))
        print(self.__statistics["all-recovery-units-busy"].get_confidence_interval_as_str("Busy"))
        print(self.__statistics["usage_of_operation_unit"].get_confidence_interval_as_str("Usage"))
        print("-" * 150)



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



    def __collect_statistics(self, env, interval):
        """
            Monitor process.
        """
        while True:
            yield env.timeout(interval)
            Statistics.update_sample("usage_of_operation_unit",   [env.now, self.__operation.resources.count / self.__operation.resources.capacity * 100.0])
            Statistics.update_sample("length_entrance_queue",     [env.now, len(self._waiting_list)])
            Statistics.update_sample("arrival-queue-length",      [env.now, len(self._waiting_list)])
            Statistics.update_sample("idle-capacity-preparation", [env.now, self.__preparation.resources.capacity - self.__preparation.resources.count])
            Statistics.update_sample("all-recovery-units-busy",   [env.now, 100 if self.__recovery.resources.capacity == self.__recovery.resources.count else 0])
        

    def on_patient_status_changed(self, status, patient, time_stamp):
        """
            Callback to collect statistics when patient status is changed.
        """

        if status == PatientStatus.WAITING:
            self._waiting_list.append(patient)
        elif status == PatientStatus.IN_PREPARATION:
            self._waiting_list.remove(patient)
        elif status == PatientStatus.PREPARED:
            Statistics.update_sample("number_of_prepared")
        elif status == PatientStatus.OPERATED:
            Statistics.update_sample("number_of_operated")
            #StatisticsCollection.update_statistic("rate-blocking-operations", [time_stamp,  1 if self.__recovery.resources.capacity == self.__recovery.resources.count  else 0])
            Statistics.update_sample("rate-blocking-operations", [time_stamp, 100 if self.__recovery.resources.capacity == self.__recovery.resources.count  else 0])
        elif status == PatientStatus.RECOVERED:
            Statistics.update_sample("mean_time_per_prepare", patient.time_stamps[PatientStatus.PREPARED] - patient.time_stamps[PatientStatus.WAITING])
            Statistics.update_sample("mean_time_per_operate", patient.time_stamps[PatientStatus.OPERATED] - patient.time_stamps[PatientStatus.PREPARED])
            Statistics.update_sample("mean_time_per_patient", patient.time_stamps[PatientStatus.RECOVERED] - patient.time_stamps[PatientStatus.WAITING])
            Statistics.update_sample("number_of_recovered")
        elif status == PatientStatus.DECEASED:
            Statistics.update_sample("number_of_deceased")

