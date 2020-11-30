# Assignment 4

## Serial correlation

To analyze serial correlation between the samples, scenario with following parameters was used:  
- Patient generation was based on exponential distribution and mean of 25 time units.
- Number of prepration units was 3.
- Number of operatoin units was 1.
- Number of recovery units was 4.
- Preparation time was based on exponential distribution with mean of 40 time units.
- Operation time was based on exponential distribution with mean of 20 time units.
- Recovery time was based on uniform distribution between 40 and 50 time units.

Correlation analysis was divided into two experiments:
- Experiment with fixed sample length and different sampling intervals:
  - Length of a invidual sample was 1000 time units.
  - Sampling intervals: 0, 100, 200, 300, 400, 500, 750, 1000, 1500, 2000, 2500, 3000, 4000, 5000, 6000, 7000, 8000, 9000, 10000 time units.
- Experiment with fixed sampling interval and different sample lengths:
  - Sampling interval was 5000.
  - Length of a invidual sample: 100, 200, 400, 600, 800, 1000, 1200, 1400, 1600, 1800, 2000, 2200, 2400, 2500, 3000, 3500, 4000, 4500, 5000, 6000 time units. 

### Results
Chart showing correlation presented below is from [covariances](covariances.xlsx) excel sheet, where full calculations can be found. 

![Correlation](./correlation_sample_interval.png)

Chart showing correlation presented below is from [covariances_length](covariances-length.xlsx) excel sheet, where full calculations can be found. 
![Correlation](./correlation_sample_length.png)

The results show that with higher interval (≥8000 time units) between invidual samples, correlation between the samples is negligible. In addition to interval between the samples, sample length affects the correlation as smaller sample lengths shows higher correlation between the samples.

**Note: 20 samples were taken for each simulation run, also Unif(40,50) was used for recovery units.**

## Regression model

Based on correlation analysis, sampling interval 10000 was used.

### Personal twist

To analyze the effect of personal twist, following parameters where used to add personal twist:
- Patients with two conditions are generated:
  - MILD condition.
  - CRITICAL condition.
- From the total number of generated patients 90 % are in MILD condition and 10 % in CRITICAL condition.
- Patients in CRITICAL condition has higher priorization in queues.
- Patients in CRITICAL condition has 20 % to die during prepration or operation.
  - This is true in ideal situtation where patient is not waiting to enter preparaton or operation.
  - Probability to die before or during operation is dependent on total time elapsed; with 20% probability to die in ideal conditiosn, patient has average of 100% probability to die if patient is waiting time is four times the total time it takes in ideal conditions patient to be operated.
- Patient in CRITICAL condition has different service time multipliers:
  - Preparation time multiplier is 0.6.
  - Operation time multiplier is 1.2.
  - Recovery time multiplier is 1.6.
  
In configuration file, patient conditions are defined as:
```
patient-condition-MILD:     [1, 0.9, 0.0, [1.0, 1.0, 1.0]]
patient-condition-CRITICAL: [0, 0.1, 0.2, [0.6, 1.2, 1.6]]
```
