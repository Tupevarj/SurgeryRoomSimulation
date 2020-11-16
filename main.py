from Simulations.SurgerySimulation import SurgerySimulator
from Core.Exceptions import SimulationException

def main():
    try:
        simulation = SurgerySimulator()
    except SimulationException as e:
        print(e)
        print("Critical error occured, see above, exiting simulation..")

"""
    TODO: Simulator multi dispatcher...
"""

if __name__ == '__main__':
    main()