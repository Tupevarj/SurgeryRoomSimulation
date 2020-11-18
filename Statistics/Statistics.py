from Core.Exceptions import SimulationException
from abc import ABCMeta, abstractmethod


class CounterStatistic:

    def __init__(self, description, unit="", formatter = lambda values : "{:80}: {} {}".format(*values)):
        self._counter = 0
        self._description = description
        self._unit = unit
        self._formatter = formatter

    def update(self):
        self._counter += 1

    def __str__(self):
        return self._formatter([self._description, self._counter, self._unit])


class ScalarStatistic:

    def __init__(self, description, unit="", formatter = lambda values : "{:80}: {} {}".format(*values)):
        self._value = 0
        self._description = description
        self._unit = unit
        self._formatter = formatter

    def update(self, value):
        self._value += value

    def __str__(self):
        return self._formatter([self._description, self._value, self._unit])
    

class ScalarMeanStatistic:

    def __init__(self, description, unit="", formatter = lambda values : "{:80}: {:.2f} {}".format(*values)):
        self._value = 0
        self._counter  = 0
        self._description = description
        self._unit = unit
        self._formatter = formatter

    def update(self, value):
        self._value += value
        self._counter += 1

    def __str__(self):
        return self._formatter([self._description, self._value * 1.0 / self._counter, self._unit])


class TableStatistic:

    def __init__(self, description, titles, formatter = None):
        self._titles = titles
        self._description = description
        self._values = []
        self._formatter = self._table_to_string if formatter is None else formatter

    def update(self, value):
        self._values.append(value)

    def __str__(self):
        return self._formatter(self._values)

    def _table_to_string(self, values):
        """
            Default formatter, returns table with header and data rows.
        """
        widths = [max(len(title) + 1, 8) for title in self._titles]
        return (self._description + "\n" + "".join(["{:^" + str(w) + "}" for w in widths]) + "\n").format(*self._titles) + '\n'.join([("".join(["{:^" + str(w) + "}" for w in widths])).format(*v) for v in self._values])

    
class StatisticsOut(metaclass=ABCMeta):
    """
        Statistic output interface. TODO: Derive on that outputs to file.
    """
    def __init__(self):
        pass
    
    @abstractmethod
    def output_statistic(self, statistic, *args):
        pass

    

class StatisticsOutConsole(StatisticsOut):
    """
        Statistic output to stdout.
    """
    def __init__(self):
        pass
    
    def output_statistic(self, statistic, *args):
        print(str(statistic))

        
class StatisticsCollection:
    """
        Singleton for handling statistics.
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
        """
            Adds new statistic to the collection.
        """
        StatisticsCollection._instance.add_statistic(statistic, name)
        
    @staticmethod
    def update_statistic(name, *args):
        """
            Adds data to previously created statistic.
        """
        StatisticsCollection._instance.update_statistic(name, *args)

    @staticmethod
    def output_statistic(name, output):
        """
            Outputs statistic. Depending on <output>, could ouput to stdout or file.
        """
        StatisticsCollection._instance.output_statistic(name, output)