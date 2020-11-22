from Logging.Logging import SimLogger as Logger, LogLevel
from Statistics.Statistics import *
from enum import Enum
import random

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
    RECOVERED      = 6


class PatientRecord:

    def __init__(self, id, time_stamp, patient_status_changed_callback, times):
        self.id = id
        self.time_stamps = dict()
        self._callback = patient_status_changed_callback
        self.update_status(PatientStatus.WAITING, time_stamp)
        
        self.preparation_time = times[PatientStatus.IN_PREPARATION]
        self.operation_time   = times[PatientStatus.IN_OPERATION] 
        self.recovery_time    = times[PatientStatus.IN_RECOVERY]

    def update_status(self, status, time_stamp):
        self.time_stamps[status] = time_stamp
        Logger.log(LogLevel.DEBUG, "Patient (id: " + str(self.id) + ") is " + str(status).split(".")[1].lower().replace("_", " ") + ".")
        self._callback(status, self, time_stamp)


class PatientRecords:
    """
        Class handling patient statistics collecting. TODO: Could remove recovered patients by wrapping callback.
    """
    _NEXT_ID = 0

    def __init__(self, patient_status_changed_callback):
        self._patients = []
        self._callback = patient_status_changed_callback


    def add_patient(self, times, time_stamp):
        """
            Adds (creates) new patient record to patient record collection.
        """
        self._patients.append(PatientRecord(PatientRecords._NEXT_ID, time_stamp, self._callback, times))
        PatientRecords._NEXT_ID += 1
        return self._patients[-1]


class PatientGenerator:
    """
        Class for generating patients.
    """

    def __init__(self, interval, severe_portion, patient_records, times_mild, times_severe):
        self._interval = interval
        self._severe_threshold = severe_portion
        self._patients = patient_records
        self.__times_mild = times_mild
        self.__times_severe = times_severe

        self.__statistics = {
                "patient-severity-portion": ScalarMeanStatistic("True portion of severity patients", "%"),
                "patient-generator-interval": ScalarMeanStatistic("True interval of generating patients", "hours"),
                "mean-in-preparation-time": ScalarMeanStatistic("Mean preparation time based on exponential distribution.", "hours"),
                "mean-in-operation-time": ScalarMeanStatistic("Mean operation time based on exponential distribution.", "hours"),
                "mean-in-recovery-time": ScalarMeanStatistic("Mean recovery time based on exponential distribution.", "hours")
        }

        [StatisticsCollection.add_statistic(name, stat) for name, stat in self.__statistics.items()]


    def run(self, env, next_step):
        """
            Starts generating patients.
        """

        while True:
            patient = self._generate_new_patient(env)
            env.process(next_step(env, patient))

            # Get interval based expotential distribution:
            timeout = random.expovariate(1.0 / self._interval)
            yield env.timeout(timeout)

            # Update statistic:
            StatisticsCollection.update_statistic("patient-generator-interval", timeout)
            

    def _generate_new_patient(self, env):
        """
            Generates new patient with either mild or severe condition based on severe_threshold.
            NOTE: uses random for severity portion; might not produce requested portion with short simulation time.
        """

        # Randomize patient properties (severity from uniform distribution and service times from exponential distribution):
        is_severe = random.uniform(0.0, 1.0) <= self._severe_threshold
        times = {
          PatientStatus.IN_PREPARATION: random.expovariate(1.0 / (self.__times_severe[PatientStatus.IN_PREPARATION] if is_severe else self.__times_mild[PatientStatus.IN_PREPARATION])),
          PatientStatus.IN_OPERATION:   random.expovariate(1.0 / (self.__times_severe[PatientStatus.IN_OPERATION] if is_severe else self.__times_mild[PatientStatus.IN_OPERATION])),
          PatientStatus.IN_RECOVERY:    random.expovariate(1.0 / (self.__times_severe[PatientStatus.IN_RECOVERY] if is_severe else self.__times_mild[PatientStatus.IN_RECOVERY]))
        }

        # Update statistic:
        StatisticsCollection.update_statistic("patient-severity-portion", 100.0 if is_severe else 0.0)
        StatisticsCollection.update_statistic("mean-in-preparation-time", times[PatientStatus.IN_PREPARATION])
        StatisticsCollection.update_statistic("mean-in-operation-time", times[PatientStatus.IN_OPERATION])
        StatisticsCollection.update_statistic("mean-in-recovery-time", times[PatientStatus.IN_RECOVERY])

        # Add patient to patient records:
        patient = self._patients.add_patient(self.__times_severe if is_severe else self.__times_mild, env.now)
        Logger.log(LogLevel.DEBUG, "Created new patient (id: {}) with {} condition.".format(patient.id, ("severe" if is_severe else "mild")))
        return patient


    def output_statistics(self, output):
        """
            Outputs statistics collected by the patient generator.
        """
        [StatisticsCollection.output_statistic(name, output) for name in self.__statistics.keys()]

