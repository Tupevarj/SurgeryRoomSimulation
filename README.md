# Surgery Room Simulation
TIES481 Course assignment.

## Simulation

Simulates surgery facility with continuous flow of patients. Patient condition can either be mild or severe. In simulation three steps are considered:
1. Surveilled preparation phase.
2. Actual operation phase.
3. Wake up and recovery under surveillance phase.

Each of these phases has limited resources. Each patient goes through each phase and are allowed to move next phase only when next phase has free resources. Target is to find minimal amount of resources that is needed to handle each patient without excessive waiting between phases.


## Usage

Simulation configuration is provided by file, which is passed as an command line input to simulator. Parameters are key-value pairs separated by colon and space. Each parameter needs to provided in it's own line. Parameters that are not provided by the user are initialized with default values. Example syntax of configuration file:

```
PARAMETER_NAME1: PARAMETER1_VALUE
PARAMETER_NAME2: PARAMETER2_VALUE
....
```

Supported parameters and default values can be printed by calling simulator with command line argument --params. Example usage to print supported parameters:
```
python main.py --params
```

Example configuration file is included in the **Examples** folder.
Example usage:
```
python main.py --conf Examples\example-configuration.txt
```

## Requirements
Python >= 3.6  
SimPy

To install SimPy, use pip:
```
pip install simpy
```

## Documentation

**PatientGenerator** creates single patient in given interval based on **patient-interval** parameter value. Once patient is generated, patient is moved into preparation phase (**PreparationUnits**) when preparation unit has free resources. Amount of resources in prepration unit can be given with **number-of-preparation-unit** parameter. Once preparation phase is completed (based on **preparation-time-** parameters), patient is moved into operation phase (**OperationUnits**) when operation unit has free resources. Amount of resources in operation unit can be given with **number-of-operation-unit** parameter. Once operation phase is completed (based on **operation-time-** parameters), patient is moved into recovery phase (**RecoveryUnits**) when recovery unit has free resources. Amount of resources in recovery unit can be given with **number-of-recovery-unit** parameter. After recovery phase is completed, patient is released. After simulation is completed (based on **simulation-time** parameter), statistics collected during the simulation are shown. By default all statistics are enabled.

## Personal Twist

Generated patients can have different conditions. Patient condition determines the urgency (priorization), risk to die during or before operation and custom service times for each phase. Different conditions and proportions of total generated number of patients can be changed in configuration file.


## Assignment

Assignment 3 results are available in Examples\Assignments\A3 folder..  
Assignment 4 results are available in Examples\Assignments\A4 folder..

...
