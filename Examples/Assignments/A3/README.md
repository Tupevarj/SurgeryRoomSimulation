# Assignment 3

## Point estimates with condidence levels

### Scenario 1 (3 preparation, 4 recovery):
```
Utilization of the operation theater                                              82.09 +- 1.62 %
Patients at the arrival queue                                                      0.84 +- 0.53
Idle capacity at prepration                                                        0.60 +- 0.12
Moving to recovery blocked                                                         5.34 +- 1.72 %
All recovery units are busy                                                        6.53 +- 1.42 %
```

Full statistics collected from the simulation are in **3p4r_statistics** excel sheet.

### Scenario 2 (3 preparation, 5 recovery):
```
Utilization of the operation theater                                              80.82 +- 1.51 %
Patients at the arrival queue                                                      0.80 +- 0.49
Idle capacity at prepration                                                        0.61 +- 0.12
Moving to recovery blocked                                                         0.87 +- 0.53 %
All recovery units are busy                                                        1.12 +- 0.43 %
```

Full statistics collected from the simulation are in **3p5r_statistics** excel sheet.

### Scenario 3 (4 preparation, 5 recovery):
```
Utilization of the operation theater                                              81.04 +- 2.12 %
Patients at the arrival queue                                                      0.28 +- 0.17
Idle capacity at prepration                                                        1.51 +- 0.18
Moving to recovery blocked                                                         1.13 +- 0.58 %
All recovery units are busy                                                        1.32 +- 0.58 %
```

Full statistics collected from the simulation are in **4p5r_statistics** excel sheet.


## Observed values differ from scenario to scenario

In the first scenario the utilization of a recovery units (**All recovery units are busy**) and moving to recovery being blocked statistics are 
significantly higher than in two other scenarios. This is expected as number of recovery units in the first scenario is lower than two 
other scenarios.

In the third scenario number of patients at the arrival queue is significantly lower and idle capcity of preparion units is significantly
higher than in two other scenarios. This is expected as number of prepatoin units in the third scenario is higher than two 
other scenarios. Also in the third scenario idle capcity of prepation units has better confidence level than any other statistic.

**Note: same random seed was used for each scenario by default.**

## Difference between scenarios

Results for difference between scenarios presented below are based on calculations carried in [pairwise_comparison](pairwise_comparison.xlsx)**** excel sheet.

### Scenario 1 (3 preparation, 4 recovery) vs scenario 2 (3 preparation, 5 recovery):

```
Utilization of the operation theater                                               1.28 +- 0.51 %
Patients at the arrival queue                                                      0.04 +- 0.05
Idle capacity at prepration                                                        0.00 +- 0.02
Moving to recovery blocked                                                         4.41 +- 1.56 %
All recovery units are busy                                                        5.41 +- 1.16 %
```

### Scenario 1 (3 preparation, 4 recovery) vs scenario 3 (4 preparation, 5 recovery):

```
Utilization of the operation theater                                               1.06 +- 0.85 %
Patients at the arrival queue                                                      0.56 +- 0.39
Idle capacity at prepration                                                       -0.91 +- 0.08
Moving to recovery blocked                                                         4.25 +- 1.81 %
All recovery units are busy                                                        5.21 +- 1.11 %
```

### Scenario 2 (3 preparation, 5 recovery) vs scenario 3 (4 preparation, 5 recovery):

```
Utilization of the operation theater                                              -0.22 +- 0.83 %
Patients at the arrival queue                                                      0.52 +- 0.35
Idle capacity at prepration                                                       -0.90 +- 0.08
Moving to recovery blocked                                                        -0.17 +- 0.72 %
All recovery units are busy                                                       -0.20 +- 0.48 %
```


## Personal twist scenario

Same expected overall utilization rate for operating room can get by changing patient generator to generate
patients in three conditions; in MILD, SEVERE and CRITICAL conditions, with following parameters:

75% of total patients are in MILD condition and 20% are in SEVERE condition and 5% are in CRITICAL condition.\
Patient in all conditions have same urgency (1), death rate (0),  operation and recovery times.\
Patients in MILD condition have 0.7 preparation time multiplier.\
Patients in SEVERE condition have 1.6 preparation time multiplier.\
Patients in CRITICAL condition have 3.1 preparation time multiplier.

In configuration file, it is configured as below:

```
patient-condition-MILD:     [1, 0.75, 0.0, [0.7, 1.0, 1.0]]
patient-condition-SEVERE:   [1, 0.20, 0.0, [1.6, 1.0, 1.0]]
patient-condition-CRITICAL: [1, 0.05, 0.0, [3.1, 1.0, 1.0]]
```


Configuration with personal twist results:

### With 3 preparation, 4 recovery
```
Utilization of the operation theater                                              75.13 +- 5.09 %
Patients at the arrival queue                                                     58.86 +- 17.90
Idle capacity at prepration                                                        0.00 +- 0.01
Moving to recovery blocked                                                         3.39 +- 1.03 %
All recovery units are busy                                                        4.55 +- 0.99 %
```

### With 3 preparation, 5 recovery:
```
Utilization of the operation theater                                              73.84 +- 4.75 %
Patients at the arrival queue                                                     57.46 +- 17.84
Idle capacity at prepration                                                        0.00 +- 0.01
Moving to recovery blocked                                                         0.50 +- 0.37 %
All recovery units are busy                                                        0.76 +- 0.33 %
```

### With 4 preparation, 5 recovery:
```
Utilization of the operation theater                                              80.16 +- 2.64 %
Patients at the arrival queue                                                      1.39 +- 0.82
Idle capacity at prepration                                                        0.49 +- 0.15
Moving to recovery blocked                                                         0.88 +- 0.67 %
All recovery units are busy                                                        0.84 +- 0.40 %
```

Mostly notable change is amount of patients at the arrival queue and thus idle capacity at the preparation units. With 3 preparation units 
as in the first and the second scenarios, number of patients at the arrival queue is significantly higher and idle capacity significantly 
lower than in third scenario, where there are 4 preparation units. Also utilization of the operation unit is below 80% with 3 preparation
units. Otherwise results with the personal twist are more aligned with thre results without personal twist, with higher utilization at the
prepration and lower utilization in later operation and recovery phases.

