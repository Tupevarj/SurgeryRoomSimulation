import simpy
import argparse
import sys
import re
from Core.Parameters import SimulationParameters


def parse_arguments():
    parser = argparse.ArgumentParser(description='Simulation configuration are provided by single file.')
    parser.add_argument('--conf', 
                        type=argparse.FileType('r'), 
                        default=sys.stdin,
                        help='File containing parameters used in simulator.')
    return parser.parse_args()


def main():

    # Print custom error message if correct path is not provided:
    try:
        conf_file = parse_arguments()
    except:
        print("Please provide correct path to file containing simulation configuration by '--conf' command line option")
        sys.exit()

    # Parse arguments for simulation:
    parameter = SimulationParameters(conf_file.conf.readlines())

    # TODO: Initialize simulator with parameters:
    

    conf_file.conf.close()
    


if __name__ == '__main__':
    main()