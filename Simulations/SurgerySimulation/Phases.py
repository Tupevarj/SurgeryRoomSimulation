from abc import ABCMeta, abstractmethod
from Logging.Logging import Logger, LogLevel
from Simulations.SurgerySimulation.Patients import PatientRecord, PatientStatus

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
        

class PreparationUnits(SimulationPhase):
    """
        Preparation units: prepares patient for a operation, limited places.
    """
    
    def __init__(self, units, next_step, time_mild, time_severe):
        super().__init__(next_step, units)
        self._time_mild = time_mild
        self.time_severe = time_severe

    
    def execute_phase(self, env, patient):
        
        patient.update_status(PatientStatus.IN_PREPARATION, env.now)
        yield env.timeout(self.time_severe if patient.is_severe else self._time_mild)
        patient.update_status(PatientStatus.PREPARED, env.now)


class OperationUnits(SimulationPhase):
    """
        Operation places: handles operation of a patient, after operation patient is moved to recovery, limited places.
    """

    def __init__(self, units, next_step, time_mild, time_severe):
        super().__init__(next_step, units)
        self._time_mild = time_mild
        self.time_severe = time_severe
    

    def execute_phase(self, env, patient):
        patient.update_status(PatientStatus.IN_OPERATION, env.now)
        yield env.timeout(self.time_severe if patient.is_severe else self._time_mild)
        patient.update_status(PatientStatus.OPERATED, env.now)


class RecoveryUnits(SimulationPhase):
    """
        Recovery places: handles recovery of a patient, limited places.
    """

    def __init__(self, units, time_mild, time_severe):
        super().__init__(None, units)
        self._time_mild = time_mild
        self.time_severe = time_severe

    
    def execute_phase(self, env, patient):
        patient.update_status(PatientStatus.IN_RECOVERY, env.now)
        yield env.timeout(self.time_severe if patient.is_severe else self._time_mild)
        patient.update_status(PatientStatus.RECOVERED, env.now)

        # TODO: Statistics here
