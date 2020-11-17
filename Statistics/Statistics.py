from Core.Exceptions import SimulationException
from abc import ABCMeta, abstractmethod


class CounterStatistic:

    def __init__(self, description, unit=""):
        self._counter = 0
        self._description = description
        self._unit = unit

    def update(self):
        self._counter += 1

    def get_value(self):
        return self._counter
    
    def get_description(self):
        return self._description

    def get_unit(self):
        return self._unit


class ScalarStatistic:

    def __init__(self, description, unit=""):
        self._value = 0
        self._description = description
        self._unit = unit

    def update(self, value):
        self._value += value

    def get_value(self):
        return self._value
    
    def get_description(self):
        return self._description

    def get_unit(self):
        return self._unit

    
class ScalarMeanStatistic:

    def __init__(self, description, unit=""):
        self._value = 0
        self._counter  = 0
        self._description = description
        self._unit = unit

    def update(self, value):
        self._value += value
        self._counter += 1

    def get_value(self):
        return self._value * 1.0 / self._counter
    
    def get_description(self):
        return self._description
    
    def get_unit(self):
        return self._unit

class TimeStampStatistic:

    def __init__(self):
        self._values = []

    def update(self, id, timestamp):
        self._values.append((id, timestamp))


class StatisticsOut(metaclass=ABCMeta):

    def __init__(self):
        pass
    
    @abstractmethod
    def output_statistic(self, statistic, *args):
        pass

    

class StatisticsOutConsole(StatisticsOut):

    def __init__(self):
        pass
    
    def output_statistic(self, statistic, *args):
        
        if isinstance(statistic, CounterStatistic):
            print((statistic.get_description() +  ":").ljust(50, ' '), str(statistic.get_value()).rjust(10, ' '), statistic.get_unit())
        elif isinstance(statistic, ScalarMeanStatistic):
            print((statistic.get_description() +  ":").ljust(50, ' '), f'{statistic.get_value():.2f}'.rjust(10, ' '), statistic.get_unit())

        
class StatisticsCollection:
    """
        Singleton for handling statistics.

        NOTE: NOW STORES EVERYTHING ON RAM, UNTIL FLUSHED! TODO: output to files.
    """
    
    _instance = None

    class __StatisticsCollection:
        """
            Nested class needed for singleton pattern.
        """
        def __init__(self):
            self._statistics = dict()
            
        def add_statistic(self, statistic, name):
            if name in self._statistics:
                raise SimulationException("Statistics '" + str(name) + "' already exists.")
            self._statistics[name] = statistic

        def update_statistic(self, name, *args):
            if name not in self._statistics:
                raise SimulationException("Statistics '" + str(name) + "' does not exist.")
            self._statistics[name].update(*args)

        def output_statistic(self, name, output):
            if name not in self._statistics:
                raise SimulationException("Statistics '" + str(name) + "' does not exist.")
            output.output_statistic(self._statistics[name])


    def __init__(self):
        if StatisticsCollection._instance is None:
            StatisticsCollection._instance = self.__StatisticsCollection()
        
    @staticmethod
    def add_statistic(statistic, name):
        StatisticsCollection._instance.add_statistic(statistic, name)
        
    @staticmethod
    def update_statistic(name, *args):
        StatisticsCollection._instance.update_statistic(name, *args)

    @staticmethod
    def output_statistic(name, output):
        StatisticsCollection._instance.output_statistic(name, output)