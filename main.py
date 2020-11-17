from Simulations.SurgerySimulation import SurgerySimulation
from Core.Exceptions import SimulationException

def main():
    try:
        simulation = SurgerySimulation()
    except SimulationException as e:
        print(e)
        print("Critical error occured, see above, exiting simulation..")

"""
    TODO: Add statistics.
    TODO: Add simulator multi dispatcher (not funny to manyally change configuration file for each simulation).
    TODO: Log simulation times.
"""

if __name__ == '__main__':
    main()