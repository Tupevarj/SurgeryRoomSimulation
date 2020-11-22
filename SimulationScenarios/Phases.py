from abc import ABCMeta, abstractmethod
from SimulationScenarios.Patients import PatientRecord, PatientStatus

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
            Returns boolean to indicate if continue.
        """
        pass

    def enter_phase(self, env, priority, patient):
        """
            Simulation sequencer method, that takes care total execution of the phase that includes:
            - entering current phase
            - executing current phase
            - moving to next phase
        """

        # If limited resources, needs to wait until resources are available:
        if self.resources is not None:
            with self.resources.request(priority=priority) as req:
                yield req
                cont = yield env.process(self.execute_phase(env, patient))
                if cont:
                    # Need to reserve resources until next phase is free:
                    yield env.process(self._enter_next_phase(env, priority, patient))

        else:
            cont = yield env.process(self.execute_phase(env, patient))
            if cont:
                yield env.process(self._enter_next_phase(env, priority, patient))
           

    def _enter_next_phase(self, env, priority, patient):
        """
            Handles movement to next phase.
        """
        if self.next_phase is not None:
            if self.next_phase.resources is not None:
                with self.next_phase.resources.request(priority=priority) as req:
                    yield req
                    if self.next_phase is not None:
                        env.process(self.next_phase.enter_phase(env, priority, patient))
            else:
                yield env.process(self.next_phase.enter_phase(env, priority, patient))


class PreparationUnits(SimulationPhase):
    """
        Preparation units: prepares patient for a operation, limited resources.
    """
    
    def __init__(self, units, next_step):
        super().__init__(next_step, units)

    def execute_phase(self, env, patient):
        patient.update_status(PatientStatus.IN_PREPARATION, env.now)
        if patient.get_time_to_live(env.now) < patient.preparation_time:
            yield env.timeout(max(0, min(patient.preparation_time, patient.get_time_to_live(env.now))))
            patient.update_status(PatientStatus.DECEASED, env.now)
            return False
        else:
            yield env.timeout(patient.preparation_time)
     
        patient.update_status(PatientStatus.PREPARED, env.now)
        return True


class OperationUnits(SimulationPhase):
    """
        Operation units: handles operation of a patient, after operation patient is moved to recovery, limited resources.
    """

    def __init__(self, units, next_step):
        super().__init__(next_step, units)

    def execute_phase(self, env, patient):
        patient.update_status(PatientStatus.IN_OPERATION, env.now)
        if patient.get_time_to_live(env.now) < patient.operation_time:
            yield env.timeout(max(0, min(patient.operation_time, patient.get_time_to_live(env.now))))
            patient.update_status(PatientStatus.DECEASED, env.now)
            return False
        else:
            yield env.timeout(patient.operation_time)

        patient.update_status(PatientStatus.OPERATED, env.now)
        return True


class RecoveryUnits(SimulationPhase):
    """
        Recovery units: handles recovery of a patient, limited resources.
    """

    def __init__(self, units):
        super().__init__(None, units)

    def execute_phase(self, env, patient):
        patient.update_status(PatientStatus.IN_RECOVERY, env.now)
        yield env.timeout(patient.recovery_time)
        patient.update_status(PatientStatus.RECOVERED, env.now)
        return True
