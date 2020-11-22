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
        StatisticsCollection.add_statistic("patient-severity-portion",   ScalarMeanStatistic("True portion of severity patients", "%"))


    def run(self, env, next_step):
        """
            Starts generating patients.
        """
        while True:
            patient = self._generate_new_patient(env)
            env.process(next_step(env, patient))
            yield env.timeout(self._interval)
            

    def _generate_new_patient(self, env):
        """
            Generates new patient with either mild or severe condition based on severe_threshold.
            NOTE: uses random for severity portion; might not produce requested portion with short simulation time.
        """
        is_severe = random.uniform(0.0, 1.0) <= self._severe_threshold
        StatisticsCollection.update_statistic("patient-severity-portion", 1 if is_severe else 0)
        patient = self._patients.add_patient(self.__times_severe if is_severe else self.__times_mild, env.now)
        Logger.log(LogLevel.DEBUG, "Created new patient with id: " + str(patient.id) + " and " + ("severe" if is_severe else "mild") + " condition.")
        return patient

    def output_statistics(self, output):
        """
            Outputs statistics collected by the patient generator.
        """
        StatisticsCollection.output_statistic("patient-severity-portion", output)

