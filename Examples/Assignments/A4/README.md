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

Based on correlation analysis, sampling interval 10000 was used. Sample length was 1000 units.

### Experiment design

The following experiment design was used:

Run |  A |  B |  C |  D | E  |  F |
----|----|----|----|----|----|----|
 1  | +1 | +1 | +1 | +1 | +1 | +1 |
 2  | -1 | -1 | -1 | +1 | +1 | +1 |
 3  | -1 | +1 | +1 | -1 | -1 | +1 |
 4  | +1 | -1 | -1 | -1 | -1 | +1 |
 5  | +1 | -1 | +1 | -1 | +1 | -1 |
 6  | -1 | +1 | -1 | -1 | +1 | -1 |
 7  | -1 | -1 | +1 | +1 | -1 | -1 |
 8  | +1 | +1 | -1 | +1 | -1 | -1 |

Which translated to the cofigurations and results:

|experiment | Distr | Rate    | Prep time   | Rec Time    | Nprep | Nrec | Average queue length | Variance    |
|:---------:|:-----:|:-------:|:-----------:|:-----------:|:-----:|:----:|:--------------------:|:-----------:|
| 1         | exp   | 25      | exp(40)     | exp(40)     | 5     | 5    | 0,088090611          | 0,024595261 |
| 2         | unif  | (20,25) | Unif(30,50) | exp(40)     | 5     | 5    | 1,137240901          | 9,820077854 |
| 3         | unif  | (20,3)  | exp(40)     | Unif(30,50) | 4     | 5    | 0,537050571          | 2,235847939 |
| 4         | exp   | 22,5    | Unif(30,50) | Unif(30,50) | 4     | 5    | 0,070490611          | 0,007657008 |
| 5         | exp   | 22,5    | exp(40)     | Unif(30,50) | 5     | 4    | 0,379364855          | 0,284393736 |
| 6         | unif  | (20,3)  | Unif(30,50) | Unif(30,50) | 5     | 4    | 0,13378              | 0,438886436 |
| 7         | unif  | (20,25) | exp(40)     | exp(40)     | 4     | 4    | 3,705415606          | 26,78830475 |
| 8         | exp   | 25      | Unif(30,50) | exp(40)     | 4     | 4    | 0,02625002           | 0,000995825 |


Regression analysis results:

|            |   Coefficients | P-value     |
|----------- | -------------- | ----------- |
|  Intercept |  0,759710397   | 0,194595382 |
|          A | -0,618661373   | 0,23535059  |
|          B | -0,563417596   | 0,256108002 |
|          C |  0,417770014   | 0,331655518 |
|          D |  0,479538888   | 0,295129389 |
|          E | -0,325091305   | 0,404515268 |
|          F | -0,301492223   | 0,427669214 |

The linear regression model (M1) doesn't explain the results well, but the errors are much smaller, if  the least
significant factor F is dropped from the model (M2).

experiment | Average queue length | M1 predicted| M1 error     | M2 predicted | M2 error     |
---------- | -------------------- | ----------- | ------------ |------------- | ------------ |
         1 | 0,088090611          | 0,467018173 |  0,378927563 |  0,149849024 |  0,061758413 |
         2 | 1,137240901          |-0,200764437 | -1,338005338 |  1,678466934 |  0,541226034 |
         3 | 0,537050571          | 2,847020423 |  2,309969852 |  1,078276604 |  0,541226034 |
         4 | 0,070490611          |-0,074432573 | -0,144923183 |  0,132249024 |  0,061758413 |
         5 | 0,379364855          | 0,281660756 | -0,097704099 |  0,317606441 | -0,061758413 |
         6 | 0,13378              | 1,284958201 |  1,151178201 | -0,407446034 | -0,541226034 |
         7 | 3,705415606          | 1,361297785 | -2,34411782  |  3,164189572 | -0,541226034 |
         8 | 0,02625002           | 0,110924845 |  0,084674825 | -0,035508393 | -0,061758413 |

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
Design matrix:

| 1 | Arr dist  | Arr mean  | Prep time | Reco time | Prep num | Condition  |
|:-:|:---------:|:---------:|:---------:|:---------:|:--------:|:----------:|
| 1 |  1   |  1   |  1   |  1   |  1   |   1   |
| 1 | -1   | -1   | -1   |  1   |  1   |   1   |
| 1 | -1   |  1   |  1   | -1   | -1   |   1   |
| 1 |  1   | -1   | -1   | -1   | -1   |   1   |
| 1 |  1   | -1   |  1   | -1   |  1   |  -1   |
| 1 | -1   |  1   | -1   | -1   |  1   |  -1   |
| 1 | -1   | -1   |  1   |  1   | -1   |  -1   |
| 1 |  1   |  1   | -1   |  1   | -1   |  -1   |

