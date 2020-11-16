# Surgery Room Simulation
TIES481 Course assignment.

## Simulation

Simulates surgery facility with continuous flow of patients. In simulation three steps are considered:
1. Surveilled preparation phase.
2. Actual operation phase.
3. Wake up and recovery under surveillance phase.

## Usage

Simulation configuration is provided by file, which is passed as an command line input to simulator. Parameters are key-value pairs separated by colon:

PARAMETER_NAME1: PARAMETER1_VALUE\
PARAMETER_NAME2: PARAMETER2_VALUE\
....

Supported parameters can be printed by calling simulator with command line argument --params. Example of configuration file is included in the examples folder.


## Requirements
SimPy
