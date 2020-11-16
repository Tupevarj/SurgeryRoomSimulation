from abc import ABCMeta, abstractmethod
from Logging.Logging import Logger, LogLevel
from Simulators.SurgerySimulation.Patients import Patient, PatientStatus

# Scheduler
class SimulationPhase(metaclass=ABCMeta):
    """
        Simple base class for simulation phases.
    """

    def __init__(self, next_phase, resources = None):
        self.next_phase = next_phase
        self.resources = resources

    
    @abstractmethod
    def execute_phase(self, env, patient): #, *args):
        """
            Should contain all steps needed to be carried in current phase.
        """
        pass

    def enter_phase(self, env, patient):
        """
            Simulation sequencer method, that takes care total execution of the phase that includes:
            - entering current phase
            - executing current phase
            - moving to next phase
        """
        # If limited resources, needs to wait until resources are available:
        if self.resources is not None:
            with self.resources.request() as req:
                yield req
                yield env.process(self.execute_phase(env, patient))
        else:
            yield env.process(self.execute_phase(env, patient))
             
        if self.next_phase is not None:
            yield env.process(self.next_phase.enter_phase(env, patient))
        

class PreparationPlaces(SimulationPhase):
    """
        Preparation places: prepares patient for a operation, limited places.
    """

    def __init__(self, places, next_step):
        super().__init__(next_step, places)

    
    def execute_phase(self, env, patient):

        # Acquire preparation place of patient:
        Logger.log(LogLevel.DEBUG, "Patient with id: " + str(patient.id) + " has arrived to preparation.")
        yield env.timeout(1)
        Logger.log(LogLevel.DEBUG, "Patient with id: " + str(patient.id) + " has been prepared.")
        patient.record.status = PatientStatus.PREPARED


class OperationPlaces(SimulationPhase):
    """
        Operation places: handles operation of a patient, after operation patient is moved to recovery, limited places.
    """

    def __init__(self, places, next_step):
        super().__init__(next_step, places)
    

    def execute_phase(self, env, patient):
        Logger.log(LogLevel.DEBUG, "Patient with id: " + str(patient.id) + " has arrived to operation.")
        yield env.timeout(2)
        Logger.log(LogLevel.DEBUG, "Patient with id: " + str(patient.id) + " has been operated.")
        patient.record.status = PatientStatus.OPERATED


class RecoveryPlaces(SimulationPhase):
    """
        Recovery places: handles recovery of a patient, limited places.
    """

    def __init__(self, next_step):
        super().__init__(next_step, None)

    
    def execute_phase(self, env, patient):
        Logger.log(LogLevel.DEBUG, "Patient with id: " + str(patient.id) + " has arrived to recovery.")
        yield env.timeout(2)
        Logger.log(LogLevel.DEBUG, "Patient with id: " + str(patient.id) + " has recovered.")
        patient.record.status = PatientStatus.RECOVERED

        # TODO: Statistics here

