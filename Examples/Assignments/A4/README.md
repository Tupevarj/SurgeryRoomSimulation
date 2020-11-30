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
- Length of a invidual sample was 1000 time units.
- Different sampling intervals: 0, 100, 200, 300, 400, 500, 750, 1000, 1500, 2000, 2500, 3000, 4000, 5000, 6000, 7000, 8000, 9000, 10000 time units.

Chart showing correlation presented below is from [correlation](covariances.xlsx) excel sheet, where full calculations can be found. 

![Correlation](./correlation_sample_interval.png)

The results show that with higher interval (>= 8000 time units) between invidual samples, correlation between the samples is negligible.

**Note: 20 samples were taken for each simulation run, also Unif(40,50) was used for recovery units.**

## Regression model

Based on correlation analysis, sampling interval 10000 was used.
