from Logging.Logging import Logger, LogLevel
from Statistics.Statistics import *
from enum import Enum
import random

class PatientStatus(Enum):
    WAITING        = 0,
    IN_PREPARATION = 1,
    PREPARED       = 2,
    IN_OPERATION   = 3,
    OPERATED       = 4,
    IN_RECOVERY    = 5,
    RECOVERED      = 6


class PatientRecord:

    
    def __init__(self, id, is_severe, time_stamp, patient_status_changed_callback):
        self.id = id
        self.is_severe = is_severe
        self.time_stamps = { PatientStatus.WAITING: time_stamp }
        self._callback = patient_status_changed_callback

    def update_status(self, status, time_stamp):
        self.time_stamps[status] = time_stamp
        Logger.log(LogLevel.DEBUG, "Patient (id: " + str(self.id) + ") is " + str(status).split(".")[1].lower().replace("_", " ") + ".")
        self._callback(id, status)


class PatientRecords:
    """
        Class handling patient statistics collecting.
    """
    NEXT_ID = 0
    STATISTICS = { "number_of_prepared": ScalarStatistic("Number of patients PREPARED in total") }
                    #"number_of_}

    def __init__(self):
        self._patients = []

        for stat in PatientRecords.STATISTICS.items():
            StatisticsCollection.add_statistic(stat[1], stat[0])

    def add_patient(self, is_severe, time_stamp):
        self._patients.append(PatientRecord(PatientRecords.NEXT_ID, is_severe, time_stamp, self.on_patient_status_changed))
        PatientRecords.NEXT_ID += 1
        return self._patients[-1]

    def on_patient_status_changed(self, id, status):
        
        if status == PatientStatus.PREPARED:
            StatisticsCollection.update_statistic("number_of_prepared")
        #pass



class PatientGenerator:
    """
        Class for generating patients.
    """

    def __init__(self, interval, severe_portion):
        self._interval = interval
        self._severe_threshold = severe_portion
        self._patients = PatientRecords()


    def run(self, env, next_step):

        while True:
            patient = self._generate_new_patient(env)
            env.process(next_step(env, patient))
            yield env.timeout(self._interval)


    def _generate_new_patient(self, env):
        """
            Generates new patient with either mild or severe condition based on severe_threshold.
            TODO: Not use random, might not produce requested portion. Maybe use random for first patient
                  and calculate next patients condition to match requested portion.
        """

        patient = self._patients.add_patient(random.uniform(0.0, 1.0) <= self._severe_threshold, env.now)
        Logger.log(LogLevel.DEBUG, "Created new patient with id: " + str(patient.id) + " and " + ("severe" if patient.is_severe else "mild") + " condition.")
        return patient
