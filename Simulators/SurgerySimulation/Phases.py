from abc import ABC, abstractmethod
from Logging.Logging import Logger, LogLevel
from Simulators.SurgerySimulation.Patients import Patient, PatientStatus

class SimulationPhase(ABC):

    def __init__(self, next_phase, resources = None):
        self.next_phase = next_phase
        self.resources = resources

    @abstractmethod
    def enter_phase(self, env, patient): #, *args):
        pass
    

class PreparationPlaces(SimulationPhase):

    def __init__(self, next_step):
        super().__init__(next_step, None)

    
    def enter_phase(self, env, patient):
        Logger.log(LogLevel.DEBUG, "Patient with id: " + str(patient.id) + " has arrived to preparation.")
        with self.next_phase.resources.request() as req:
            yield req
            patient.record.status = PatientStatus.PREPARED
            Logger.log(LogLevel.DEBUG, "Patient with id: " + str(patient.id) + " has been prepared.")
            yield env.process(self.next_phase.enter_phase(env, patient))


class OperationPlaces(SimulationPhase):

    def __init__(self, places, next_step):
        super().__init__(next_step, places)
    

    def enter_phase(self, env, patient):
        Logger.log(LogLevel.DEBUG, "Patient with id: " + str(patient.id) + " has arrived to operation.")
        yield env.timeout(2)
        Logger.log(LogLevel.DEBUG, "Patient with id: " + str(patient.id) + " has been operated.")
        patient.record.status = PatientStatus.OPERATED

        with self.next_phase.resources.request() as req:
            yield req
            yield env.process(self.next_phase.enter_phase(env, patient))

    
class RecoveryPlaces(SimulationPhase):

    def __init__(self, places, next_step):
        super().__init__(next_step, places)

    
    def enter_phase(self, env, patient):
        Logger.log(LogLevel.DEBUG, "Patient with id: " + str(patient.id) + " has arrived to recovery.")
        yield env.timeout(2)
        Logger.log(LogLevel.DEBUG, "Patient with id: " + str(patient.id) + " has recovered.")
        patient.record.status = PatientStatus.RECOVERED
