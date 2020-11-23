from Core.Logging.Logging import SimLogger as Logger, LogLevel
from Core.Distributions import RandomGenerator as Random
from Core.Statistics.Statistics import *
from enum import Enum
import ast
import sys

class PatientStatus(Enum):
    """
        Enum for patient status.
    """
    WAITING        = 0,
    IN_PREPARATION = 1,
    PREPARED       = 2,
    IN_OPERATION   = 3,
    OPERATED       = 4,
    IN_RECOVERY    = 5,
    RECOVERED      = 6,
    DECEASED       = 7,
    


class PatientCondition:
    """
        Class for parsing and storing user provided patient conditions.
    """
    def __init__(self, string):
        conditions = ast.literal_eval(string)
        self.urgency = conditions[0]
        self.portion = conditions[1]
        self.death_rate = conditions[2]
        self.service_times = conditions[3]


    def __repr__(self):
        return "[{}, {}, {}, [{}, {}, {}]]".format(self.urgency, self.portion, self.death_rate, self.service_times[0], self.service_times[1], self.service_times[2])



class PatientRecord:
    """
        Patient record (a.k.a patient).
    """
    def __init__(self, id, time_stamp, patient_status_changed_callback, priority, times, time_to_live):
        self.id = id
        self.time_stamps = dict()
        self._callback = patient_status_changed_callback
        self.update_status(PatientStatus.WAITING, time_stamp)
        self.preparation_time = times[PatientStatus.IN_PREPARATION]
        self.operation_time   = times[PatientStatus.IN_OPERATION] 
        self.recovery_time    = times[PatientStatus.IN_RECOVERY]
        self.priority = priority
        self.__time_to_live = time_to_live


    def update_status(self, status, time_stamp):
        self.time_stamps[status] = time_stamp
        Logger.log(LogLevel.DEBUG, "Patient (id: " + str(self.id) + ") is " + str(status).split(".")[1].lower().replace("_", " ") + ".")
        self._callback(status, self, time_stamp)


    def get_time_to_live(self, time_now):
        return self.__time_to_live - (time_now - self.time_stamps[PatientStatus.WAITING])


class PatientRecords:
    """
        Class handling patient statistics collecting. TODO: Could remove recovered patients by wrapping callback.
    """
    _NEXT_ID = 0

    def __init__(self, patient_status_changed_callback):
        self._patients = []
        self._callback = patient_status_changed_callback
        self.__random = Random.new_generator()     # Independent RNG


    def add_patient(self, urgency, death_rate, times, time_stamp):
        """
            Adds (creates) new patient record to patient record collection.
        """
        # Time until patient is operated (when no waiting): 
        time_to_live = float("inf")
        if death_rate > 0:
            div = self.__random.expovariate(1.0 / death_rate)
            if div != 0:
                time_to_live = (1.0 / div * (times[PatientStatus.IN_PREPARATION] + times[PatientStatus.IN_OPERATION]))

        self._patients.append(PatientRecord(PatientRecords._NEXT_ID, time_stamp, self._callback, urgency, times, time_to_live))
        PatientRecords._NEXT_ID += 1
        return self._patients[-1]



class PatientGenerator:
    """
        Class for generating patients.
    """

    def __init__(self, interval, patient_records, base_times, patient_types):
        self._interval = interval
        self._patients = patient_records
        self.__patient_types = patient_types
        self.__base_times = base_times
        self.__random = Random.new_generator()     # Independent RNG

        sum_of_probabilities = sum(self.__patient_types[k].portion for k in self.__patient_types.keys())

        # Store probabilites to generate certain type in a lookup table:
        self.__generator_table = []
        probability_accum = 0.0
        for k, v in self.__patient_types.items():
            probability_accum += (v.portion / sum_of_probabilities)
            self.__generator_table.append([probability_accum, k])
        self.__generator_table[-1][0] = 1.0

        #self.__statistics = {  **{ "patient-portion-" + k: ScalarMeanStatistic("True portion of {} patients".format(k), "%") for k in self.__patient_types.keys()}, 
        #                       **{
        #                           "patient-generator-interval": ScalarMeanStatistic("True interval of generating patients", "hours"),
        #                           "mean-in-preparation-time": ScalarMeanStatistic("Mean preparation time based on exponential distribution.", "hours"),
        #                           "mean-in-operation-time": ScalarMeanStatistic("Mean operation time based on exponential distribution.", "hours"),
        #                           "mean-in-recovery-time": ScalarMeanStatistic("Mean recovery time based on exponential distribution.", "hours"),
        #                           "total-number-of-patients": CounterStatistic("Total number of patients generated.", "")
        #                    }}

        #try:
        #    [StatisticsCollection.register_statistic(name) for name, stat in self.__statistics.items()]
        #    [StatisticsCollection.add_statistic(name, stat) for name, stat in self.__statistics.items()]
        #except:
        #    pass


    def run(self, env, next_step):
        """
            Starts generating patients.
        """

        while True:
            patient = self._generate_new_patient(env)
            env.process(next_step(env, patient.priority, patient))

            # Get interval based expotential distribution:
            timeout = self.__random.expovariate(1.0 / self._interval)
            yield env.timeout(timeout)

            # Update statistic:
            #StatisticsCollection.update_statistic("patient-generator-interval", timeout)
            

    def _generate_new_patient(self, env):
        """
            Generates new patient with either mild or severe condition based on severe_threshold.
            NOTE: uses random for severity portion; might not produce requested portion with short simulation time.
        """

        # Randomize patient properties (condition from uniform distribution and service times from exponential distribution):
        random_uniform = self.__random.uniform(0.0, 1.0)
        condition = next(t for t in self.__generator_table if random_uniform < t[0])[1]
        times = {
          PatientStatus.IN_PREPARATION: self.__random.expovariate(1.0 / (self.__base_times[PatientStatus.IN_PREPARATION])) * self.__patient_types[condition].service_times[0],
          PatientStatus.IN_OPERATION:   self.__random.expovariate(1.0 / (self.__base_times[PatientStatus.IN_OPERATION])) * self.__patient_types[condition].service_times[1],
          PatientStatus.IN_RECOVERY:    self.__random.expovariate(1.0 / (self.__base_times[PatientStatus.IN_RECOVERY]) * self.__patient_types[condition].service_times[2])
        }

        ## Update statistic:
        #[StatisticsCollection.update_statistic2("patient-portion-" + k, 100.0 if k == condition else 0.0) for k in self.__patient_types.keys()]
        #StatisticsCollection.update_statistic2("mean-in-preparation-time", times[PatientStatus.IN_PREPARATION])
        #StatisticsCollection.update_statistic2("mean-in-operation-time", times[PatientStatus.IN_OPERATION])
        #StatisticsCollection.update_statistic2("mean-in-recovery-time", times[PatientStatus.IN_RECOVERY])
        #StatisticsCollection.update_statistic2("total-number-of-patients")

        # Add patient to patient records:
        patient = self._patients.add_patient(self.__patient_types[condition].urgency, self.__patient_types[condition].death_rate, times, env.now)
        Logger.log(LogLevel.DEBUG, "Created new patient (id: {}) in {} condition and with time to live {}.".format(patient.id, condition, patient.get_time_to_live(env.now)))
        return patient


    def output_statistics(self, output, *args):
        """
            Outputs statistics collected by the patient generator.
        """
        pass
        #StatisticsCollection.output_statistic(self.__statistics.keys(), output, *args)

