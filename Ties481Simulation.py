import simpy
import argparse
import sys
import re
from Core.Parameters import SimulationParameters
from Core.Module import ModuleBase
from Logging import LogLevel


def parse_arguments():
    parser = argparse.ArgumentParser(description='Simulation configuration are provided by single file.')
    parser.add_argument('--conf', 
                        type=argparse.FileType('r'), 
                        default=sys.stdin,
                        help='File containing parameters used in simulator.')
    return parser.parse_args()


class Simulation(ModuleBase):

    def __init__(self):

        self.LOGGER.log(LogLevel.INFO, "Creating simulation.")

        # Print custom error message if correct path is not provided:
        try:
            conf_file = parse_arguments()
        except:
            print("Please provide correct path to file containing simulation configuration by '--conf' command line option")
            sys.exit()
        
        # Parse arguments for simulation:
        parameter = SimulationParameters(conf_file.conf.readlines())
        conf_file.conf.close()


        # TODO: Initialize simulator with parameters:



def main():
    simulation = Simulation()


if __name__ == '__main__':
    main()