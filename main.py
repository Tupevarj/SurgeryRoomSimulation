from Simulations.SimulationScenarios.SimulationScenarioSurgery import SimulationScenarioSurgery
from Core.Exceptions import SimulationException

def main():
    try:
        simulation = SimulationScenarioSurgery()
    except SimulationException as e:
        print(e)
        print("Critical error occured, see above, exiting simulation..")

"""
    TODO: Add statistics.
    TODO: Add simulator multi dispatcher (not funny to manyally change configuration file for each simulation).
    TODO: Use exponential distribution.
"""

if __name__ == '__main__':
    main()