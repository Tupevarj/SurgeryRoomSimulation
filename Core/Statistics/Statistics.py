from Core.Exceptions import SimulationException
from Core.Logging.Logging import SimLogger as Logger, LogLevel
from abc import ABCMeta, abstractmethod
from enum import IntEnum, Enum
import math

"""

    Statistics Module

    Statistics can managed through Statistics singleton class.

"""

class ConfidenceInterval(IntEnum):
    
    CONFIDENCE_90 = 1645
    CONFIDENCE_95 = 1960
    CONFIDENCE_98 = 2326
    CONFIDENCE_99 = 2576


class Counter:
    """
        Stores single scalar.
    """
    def __init__(self):
        self.__value = 0
        
    def update(self, value=1):
        self.__value += value
        
    def get_value(self):
        return self.__value

    def get_count(self):
        return 1

    
class CounterMean:
    """
        Stores single scalar + counter for update calls.
    """
    def __init__(self):
        self.__value = 0
        self.__count = 0
        
    def update(self, value=1):
        self.__value += value
        self.__count += 1
        
    def get_value(self):
        return self.__value
    
    def get_count(self):
        return self.__count


class SampleCollection():
    """
        Simple collection class to hold sample of a single statistic.
    """
    
    def __init__(self, desc_l="", desc_s="", unit = "", type=CounterMean):
        """
            Default constructor, where <description_short> is column header,
            when collection is output as an table, <description_long> is
            title when collection is output as an single line.
        """
        self.__samples   = []
        self.__type      = type
        self.title_short = desc_s
        self.title_long  = desc_l
        self.unit        = unit


    def add(self):
        """
            Adds new sample to collection.
        """
        self.__samples.append(self.__type())
        return self

    def update(self, *args):
        """
            Updates last samples with data <*args>.
        """
        self.__samples[-1].update(*args)
        pass
    

    def get_value(self, sample):
        return float('nan') if self.__samples[sample].get_count() == 0 else self.__samples[sample].get_value() / self.__samples[sample].get_count()

    def get_values(self):
        return [float('nan') if s.get_count() == 0 else s.get_value() / s.get_count() for s in self.__samples]

    def get_sum(self):
        """
            Calculates sum of samples.
        """
        return sum([s.get_value() for s in self.__samples])


    def get_mean(self):
        """
            Calculates mean (average) of samples.
        """
        return self.get_sum() / sum([s.get_count() for s in self.__samples])


    def get_variance(self):
        """
            Calculates variance for samples.
        """
        mean = self.get_mean();
        return sum([((s.get_value() / s.get_count()) - mean)**2 for s in self.__samples]) / (len(self.__samples) - 1)


    def get_standard_deviation(self):
        """
            Calculates standard deviation for samples.
        """
        return math.sqrt(self.get_variance())


    def get_confidence_interval(self, level=ConfidenceInterval.CONFIDENCE_95):
        """
            Calculates confidence interval for given confidence level <level>.
        """
        return level / 1000.0 * self.get_standard_deviation() / math.sqrt(len(self.__samples))
    

class Statistics:
    """
        Singleton for storing statistics.
    """
    __instance = None
    
    def __new__(cls):
        """
            Creates singleton instance (first call only).
        """
        if Statistics.__instance is None:
            Statistics.__instance = object.__new__(cls)
            Statistics.__instance.__statistics = dict()
            Statistics.__instance.__block = True
        return Statistics.__instance


    @staticmethod
    def add_statistic(name, statistic):
        """
            Adds new statistic collection.
        """
        if name in Statistics.__instance.__statistics:
            raise SimulationException("Statistics '{}' already exists.".format(name))
        Statistics.__instance.__statistics[name] = statistic


    @staticmethod
    def start_sample():
        """
            Adds new sample to each existing statistic.
        """
        [Statistics.__instance.__statistics[name].add() for name in Statistics.__instance.__statistics.keys()]
        Statistics.__instance.__block = False
        
            
    @staticmethod
    def end_sample():
        """
            Starts blocking all update calls until new sample is started.
        """
        Statistics.__instance.__block = True


    @staticmethod
    def update_sample(name, *args):
        """
            Adds data to previously created statistic.
        """
        if not Statistics.__instance.__block:
            if name not in Statistics.__instance.__statistics:
                Logger.log(LogLevel.WARNING, "Trying to update statistic '{}', but no statistic with given name exist.".format(name))
            else:
                Statistics.__instance.__statistics[name].update(*args)

        
    @staticmethod
    def get_as_string(names, sample=None):
        """
            
        """
        for name in names:
            if name not in Statistics.__instance.__statistics:
                raise SimulationException("Statistics '{}' doesn't exist.".format(name))
        # Return mean + confidence interval of all samples:
        if sample is None:
            return "\n".join(["{:80} {:6.2f} +- {:.2f} {}".format(Statistics.__instance.__statistics[name].title_long, Statistics.__instance.__statistics[name].get_mean(), Statistics.__instance.__statistics[name].get_confidence_interval(), Statistics.__instance.__statistics[name].unit) for name in names])
        # Get single sample as str:
        return "\n".join(["{:80} {:6.2f} {}".format(Statistics.__instance.__statistics[name].title_long, Statistics.__instance.__statistics[name].get_value(sample), Statistics.__instance.__statistics[name].unit) for name in names])

        
    
    @staticmethod
    def get_as_csv(names, decimal_delimeter=","):
        """
            Returns statistics <names> as single string presenting csv table.
        """
        titles = []
        values = []
        for name in names:
            if name not in Statistics.__instance.__statistics:
                raise SimulationException("Statistics '{}' doesn't exist.".format(name))
            stat = Statistics.__instance.__statistics[name]
            titles.append("{}({})".format(stat.title_short, stat.unit))
            values.append(stat.get_values())

        return "SEP=;\n" + ";".join(titles) + "\n" + "\n".join([";".join(map(str, i)).replace(".", decimal_delimeter) for i in zip(*values)])
