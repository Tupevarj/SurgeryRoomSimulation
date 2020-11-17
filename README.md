# Surgery Room Simulation
TIES481 Course assignment.

## Simulation

Simulates surgery facility with continuous flow of patients. Patient condition can either be mild or severe. In simulation three steps are considered:
1. Surveilled preparation phase.
2. Actual operation phase.
3. Wake up and recovery under surveillance phase.


## Usage

Simulation configuration is provided by file, which is passed as an command line input to simulator. Parameters are key-value pairs separated by colon and space:

```
PARAMETER_NAME1: PARAMETER1_VALUE
PARAMETER_NAME2: PARAMETER2_VALUE
....
```

Supported parameters can be printed by calling simulator with command line argument --params. Example configuration file is included in the **Examples** folder.
Example usage:
```
python main.py --conf Examples\configuration.txt
```

Example usage to print supported parameters:
```
python main.py --params
```

## Requirements
Python >= 3.6
SimPy


## Documentation

**PatientGenerator** creates single patient in given interval (**patient-interval** parameter), where patient is moved into preparation phase (**PreparationUnits**) once free unit is available. Once preparation phase is completed (based on **preparation-time-** parameters), patient is moved into operation phase (**OperationUnits**) once free unit is available. Once operation phase is completed (based on **operation-time-** parameters), patient is moved into recovery phase (**RecoveryUnits**) once free unit is available.
After recover phase is completed, patient is released.


**TODO: Continue**


## Statistics

**TODO**
