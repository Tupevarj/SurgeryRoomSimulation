from Core.Exceptions import SimulationException
from abc import ABCMeta, abstractmethod
from enum import IntEnum
import math

"""

    Statistics Module

    Supports four different types of statistics:
    - ScalarStatistic:     Scalar statistics (single value increased by the <value> in update method).
    - CounterStatistic:    Counter statistics (counter increased by one in update method).
    - ScalarMeanStatistic: Mean scalar statistic (calculates means value of scalar).
    - TableStatistic:      Table statistics (with header and rows of values).

    Supports output to stdout (StatisticsWriterStdout) and to file (StatisticsWriterFile).

    Statistics can managed through Statistics singleton class.

"""

class ConfidenceInterval(IntEnum):
    
    CONFIDENCE_90 = 1645
    CONFIDENCE_95 = 1960
    CONFIDENCE_98 = 2326
    CONFIDENCE_99 = 2576



class ISampleScalar(metaclass=ABCMeta):
    """

    """
    def __init__(self):
        pass
    
    @abstractmethod
    def get_value(self):
        pass


class SampleScalar:
    """

    """
    __formatter = "{:80} {} {}"

    def __init__(self):
        self.__value = 0
        
    def update(self, value=1):
        self.__value += value
        
    def get_value(self):
        return self.__value

    def get_formatter(self):
        return self.__formatter

    
class SampleScalarMean:
    """

    """
    __formatter = "{:80} {:.2f} {}"

    def __init__(self):
        self.__value = 0
        self.__counter  = 0
        
    def update(self, value=1):
        self.__value += value
        self.__counter += 1

    def get_value(self):
        if self.__counter != 0:
            return self.__value / self.__counter
        return float('nan')
    
    def get_formatter(self):
        return self.__formatter


class StatisticScalar():
    
    def __init__(self, type, description, unit=""):
        self.__description = description
        self.__unit = unit
        self.__samples = []
        self.__type = type

        
    def add_sample(self, *args):
        self.__samples.append(self.__type(*args))


    def get_mean(self):
        if len(self.__samples) > 0:
            return sum([s.get_value() for s in self.__samples]) / len(self.__samples)
        return float('nan')

    
    def get_confidence_interval(self, level=ConfidenceInterval.CONFIDENCE_95):
        mean = self.get_mean()
        if not math.isnan(mean):
            stde = math.sqrt(sum([(s.get_value() - mean)**2 for s in self.__samples])  / len(self.__samples))
            return level * 0.001 * stde / math.sqrt(len(self.__values))
        return mean


    def update(self, *args):
        self.__samples[-1].update(*args)

        
    #def __getitem__(self, sample):
    #    return self.__samples[sample]

    # TODO: MOVE
    def get_sample_as_str(self, sample):
        if len(self.__samples) > sample:
            return self.__samples[sample].get_formatter().format(self.__description, self.__samples[sample].get_value(), self.__unit)



class SampleTable:

    def __init__(self):
        self.__rows   = []

    def update(self, value):
        self.__rows.append(value)

    def get_column(self, column):
        return [r[column] for r in self.__rows]
    
    def get_mean(self, column):
        return sum([r[column] for r in self.__rows])  / len(self.__rows)
    
    def __str__(self):
        return str(self.__rows)
    

class StatisticTable():


    def __init__(self, type, titles, description = ""): #, formatter = None):
        self.__description = description
        self.__titles = [t[0] if isinstance(t, list) else t for t in titles]
        self.__units =  [t[1] if isinstance(t, list) else "" for t in titles]
        self.__samples = []
        self.__type = type

    def update(self, value, sample=-1):
        self.__samples[sample].update(value)


    def add_sample(self, *args):
        self.__samples.append(self.__type(*args))


    #def __str__(self):
    #    return self._formatter(self.__values)

    #def _table_to_string(self, values):
    #    widths = [max(len(title) + 1, 8) for title in self.__titles]
    #    return ("".join(["{:^" + str(w) + "}" for w in widths]) + "\n").format(*self.__titles) + '\n'.join([("".join(["{:^" + str(w) + "}" for w in widths])).format(*v) for v in self.__values])

    #def _table_to_csv(self, values):
    #    return "SEP=,\n" +(",".join(["{}" for t in self.__titles]) + "\n").format(*self.__titles) + '\n'.join([(",".join(["{}" for t in self.__titles])).format(*v) for v in self.__values])
    
    def get_description(self):
        return self.__description

    
    def get_mean(self, column):
        col = self.__titles.index(column)
        total = sum([sum(s.get_column(col)) for s in self.__samples])
        count = sum([len(s.get_column(col)) for s in self.__samples])
        if count > 0:
            return total / count
        return float('nan')

    
    def get_confidence_interval(self, column, level=ConfidenceInterval.CONFIDENCE_95):
        col = self.__titles.index(column)
        count = sum([len(s.get_column(col)) for s in self.__samples])
        if count > 0:
            mean = sum([sum(s.get_column(col)) for s in self.__samples]) / count
            stde = math.sqrt(sum([(sum(s.get_column(col)) - mean)**2 for s in self.__samples])  / count)
            return level * 0.001 * stde / math.sqrt(count)
        return mean
    

    # TODO: Move elsewhere
    def get_sample_as_str_ci(self, sample, column, level=ConfidenceInterval.CONFIDENCE_95):
        col = self.__titles.index(column)
        if len(self.__samples) > sample:
            mean = self.get_mean(column)
            return "{:80} {:.2f} +- {:.2f} {}".format(self.__description, self.get_mean(column), self.__samples[sample].get_confidence_interval(col, mean, level), self.__units[col])

    # TODO: Move elsewhere
    def get_sample_as_str(self, sample, column):
        col = self.__titles.index(column)
        if len(self.__samples) > sample:
            return "{:80} {:.2f} {}".format(self.__description, self.__samples[sample].get_mean(col), self.__units[col])

    # TODO: Move elsewhere
    def get_mean_as_str(self, column):
        col = self.__titles.index(column)
        return "{:80} {:.2f} {}".format(self.__description, self.get_mean(column), self.__units[col])
    
    # TODO: Move elsewhere
    def get_confidence_interval_as_str(self, column, level=ConfidenceInterval.CONFIDENCE_95):
        col = self.__titles.index(column)
        return "{:80} {:.2f} +- {:.2f} {}".format(self.__description, self.get_mean(column), self.get_confidence_interval(column, level), self.__units[col])



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
        return Statistics.__instance


    @staticmethod
    def add_statistic(name, statistic):
        """
            Registers statistic group.
        """
        if name in Statistics.__instance.__statistics:
            raise SimulationException("Statistics '{}' has already been registered.".format(name))
        Statistics.__instance.__statistics[name] = statistic


    @staticmethod
    def add_sample(name, *args):
        """
            Adds new statistic to the collection.
        """
        if name not in Statistics.__instance.__statistics:
            raise SimulationException("Statistics '{}' has not been registered.".format(name))
        Statistics.__instance.__statistics[name].add_sample(*args)
        
            
    @staticmethod
    def update_sample(name, *args):
        """
            Adds data to previously created statistic.
        """
        if name not in Statistics.__instance.__statistics:
            raise SimulationException("Statistics '{}' does not exist.".format(name))
        Statistics.__instance.__statistics[name].update(*args)
        

 