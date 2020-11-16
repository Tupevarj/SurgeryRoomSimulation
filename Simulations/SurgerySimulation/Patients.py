from Logging.Logging import Logger, LogLevel
from enum import Enum
import random

class PatientStatus(Enum):
    WAITING   = 0,
    PREPARED  = 1,
    OPERATED  = 2,
    RECOVERED = 4


class PatientStatistics:
    # TODO:
    pass


class PatientRecord:

    NEXT_ID = 0
    
    def __init__(self, is_severe, time_stamp):
        self.id = PatientRecord.NEXT_ID = PatientRecord.NEXT_ID + 1
        self.is_severe = is_severe
        self.time_stamps = { PatientStatus.WAITING: time_stamp }

    def update_status(self, status, time_stamp):
        self.time_stamps[status] = time_stamp



class PatientGenerator:
    """
        Class for generating patients.
    """

    def __init__(self, interval, severe_portion):
        self._interval = interval
        self._severe_threshold = severe_portion


    def run(self, env, next_step):

        while True:
            patient = self._generate_new_patient(env)
            env.process(next_step(env, patient))
            yield env.timeout(self._interval)


    def _generate_new_patient(self, env):
        """
            Generates new patient with either mild or severe condition based on severe_threshold.
            TODO: Not use random, might not produce requested portion. Maybe use random for first patient.
        """
        patient = PatientRecord(random.uniform(0.0, 1.0) <= self._severe_threshold, env.now)
        Logger.log(LogLevel.DEBUG, "Created new patient with id: " + str(patient.id) + 
                   " and " + ("severe" if patient.is_severe else "mild") + " condition.")
        return patient
