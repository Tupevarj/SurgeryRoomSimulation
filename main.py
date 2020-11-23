from Simulation.Simulation import Simulation
from Core.Exceptions import SimulationException

def main():
    try:
        simulation = Simulation()
    except SimulationException as e:
        print(e)
        print("Critical error occured, see above, exiting simulation..")

"""

    TODO: Add simulator multi dispatcher (not funny to manyally change configuration file for each simulation).

    
    -----------------------------------------------------------------------------------------
     1.0 Simulator structure
    -----------------------------------------------------------------------------------------


    Simulation core is divided into three main modules: logging, statistics and 
    parameters modules. Mostly these modules can be considered as black boxes. 
    Basic functionality of these modules is listed below.
    
    Most of the assigment specific code is located in Simulation folder.
    This is decribed in chapter 1.4.
    
    
    -----------------------------------------------------------------------------------------
        1.1 Core/Logging module
    -----------------------------------------------------------------------------------------

    Basic logging functionality with different parameterized log levels;
    either logged into stdout or file. Usage through singleton class:
    
    Logger.log(<LogLevel>, <message>)
    
    
    -------------------------------------------------------------------------------
        1.2 Core/Statistics module
    -------------------------------------------------------------------------------

    Supports scalar and table (csv) statistics. Statistics are managed through 
    StatisticsCollection singleton class through following methods:

    StatisticsCollection.add_statistic(<Statistic>, <StatisticName>)
    StatisticsCollection.update_statistic(<StatisticName>)
    StatisticsCollection.output_statistic(<StatisticName>, <StatisticsOutput>)
    
    
    -----------------------------------------------------------------------------------------
        1.3 Core/Parameters module
    -----------------------------------------------------------------------------------------

    
    -----------------------------------------------------------------------------------------
        1.4 Simulation: TIES481 Surgery facility
    -----------------------------------------------------------------------------------------

    Phases
    Patients
    Simulation (main script)

    
    -----------------------------------------------------------------------------------------
     2.0 Personal twist
    -----------------------------------------------------------------------------------------

    Generated patients can have different conditions. Patient condition is used to
    determine:
    
    - urgency
        Urgency of patient (priority). Patients with lower priorities can jump the queue 
    - operating times
        Each condition has specific multiplier which is applied to base service times.
    - death rate:
        Patients with higher severity are at a higher risk to die during preparation
        and operation phases.

    New conditions can be created by adding new parameters with the following format:
    
         patient-condition-<NAME_OF_THE_CONDITION> : <VALUE>
    
    , where <VALUE> is array with the following elements:
      - Severity level. Lower value has higher priorization and thus higher urgency.
      - Portion of total generated patients. Sum of proportions is normalized to match 100%.
      - Death rate. Probability for patient to die before patient is operated in perfect
                    conditions (no waiting).
      - Array of multipliers for base service times.
    

    
    -----------------------------------------------------------------------------------------
     3.0 Requiremets + Usage
    -----------------------------------------------------------------------------------------

    Python >= 3.6
    SimPy

    To install SimPy, use pip (run following command in command line):

    pip install simpy


"""

if __name__ == '__main__':
    main()