# Assignment 3

## Point estimates with condidence levels:


### Scenario 1 (3 preparation, 4 recovery):
```
Patients at the arrival queue                                                    1.61 +- 0.99
Idle capacity at prepration                                                      0.85 +- 0.43
Moving to recovery blocked                                                       5.57 +- 3.66 %
All recovery units are busy                                                      5.80 +- 3.23 %
```

### Scenario 2 (3 preparation, 5 recovery):
```
Patients at the arrival queue                                                    1.56 +- 0.95
Idle capacity at prepration                                                      0.87 +- 0.44
Moving to recovery blocked                                                       0.99 +- 0.92 %
All recovery units are busy                                                      1.68 +- 1.23 %
```

### Scenario 3 (4 preparation, 5 recovery):
```
Patients at the arrival queue                                                    0.83 +- 0.56
Idle capacity at prepration                                                      1.59 +- 0.76
Moving to recovery blocked                                                       0.98 +- 1.06 %
All recovery units are busy                                                      2.01 +- 1.36 %
```


## Observed values differ from scenario to scenario

Moving to recovery blocked differs in 1st scenario, where there is one recovery unit less than in two
other scenarios.

Amount of patient at the arrival queue differes in 3rd scenario, where there is on preparaion unit
more than in two other scenarios. Also idle capacity at preparion also differs.



## Difference between scenarios

**???**



## Personal twist scenario

Same expected overall utilization rate for operating room can get by changing patient generator to generate
patients in three conditions; in MILD, SEVERE and CRITICAL conditions, with following parameters:

75% of total patients are in MILD condition and 20% are in SEVERE condition and 5% are in CRITICAL condition.\
Patient in all conditions have same urgency (1), death rate (0),  operation and recovery times.\
Patients in MILD condition have 0.7 preparation time multiplier.\
Patients in SEVERE condition have 1.6 preparation time multiplier.\
Patients in CRITICAL condition have 3.1 preparation time multiplier.\

In configuration file, its configured as below:

```
patient-condition-MILD:     [1, 0.75, 0.0, [0.7, 1.0, 1.0]]
patient-condition-SEVERE:   [1, 0.20, 0.0, [1.6, 1.0, 1.0]]
patient-condition-CRITICAL: [1, 0.05, 0.0, [3.1, 1.0, 1.0]]
```


Configuration with personal twist results:

### With 3 preparation, 4 recovery
```
Patients at the arrival queue                                                    1.61 +- 0.94
Idle capacity at prepration                                                      0.86 +- 0.43
Moving to recovery blocked                                                       5.52 +- 3.29 %
All recovery units are busy                                                      5.27 +- 2.84 %
```

### With 3 preparation, 5 recovery:
```
Patients at the arrival queue                                                    1.59 +- 0.93
Idle capacity at prepration                                                      0.87 +- 0.44
Moving to recovery blocked                                                       0.72 +- 0.85 %
All recovery units are busy                                                      1.40 +- 0.98 %
```

### With 4 preparation, 5 recovery:
```
Patients at the arrival queue                                                    0.82 +- 0.53
Idle capacity at prepration                                                      1.59 +- 0.75
Moving to recovery blocked                                                       1.68 +- 1.33 %
All recovery units are busy                                                      1.74 +- 1.25 %
```

Mostly notable change here is 'Moving to recovery blocked' statistic when there are 5 recovery
units (scenario 3).
