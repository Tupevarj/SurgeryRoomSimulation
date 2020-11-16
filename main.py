from Simulations.SurgerySimulation import SurgerySimulator
from Core.Exceptions import SimulationException

def main():
    try:
        simulation = SurgerySimulator()
    except SimulationException as e:
        print(e)
        print("Critical error occured, see above, exiting simulation..")

"""
    TODO: Add statistics.
    TODO: Add simulator multi dispatcher (not funny to manyally change configuration file for each simulation).
"""

if __name__ == '__main__':
    main()