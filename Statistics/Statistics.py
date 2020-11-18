from Core.Exceptions import SimulationException
from abc import ABCMeta, abstractmethod


class CounterStatistic:

    def __init__(self, description, unit="", formatter = "{:80}: {} {}"):
        self._counter = 0
        self._description = description
        self._unit = unit
        self._formatter = formatter

    def update(self):
        self._counter += 1

    def get_value(self):
        return self._counter
    
    def get_description(self):
        return self._description

    def get_unit(self):
        return self._unit
    
    def __str__(self):
        return self._formatter.format(self._description, self._counter, self._unit)


class ScalarStatistic:

    def __init__(self, description, unit="", formatter = "{:80}: {} {}"):
        self._value = 0
        self._description = description
        self._unit = unit
        self._formatter = formatter

    def update(self, value):
        self._value += value

    def get_value(self):
        return self._value
    
    def get_description(self):
        return self._description

    def get_unit(self):
        return self._unit
    
    def __str__(self):
        return self._formatter.format(self._description, self._value, self._unit)
    
class ScalarMeanStatistic:

    def __init__(self, description, unit="", formatter = "{:80}: {:.2f} {}"):
        self._value = 0
        self._counter  = 0
        self._description = description
        self._unit = unit
        self._formatter = formatter

    def update(self, value):
        self._value += value
        self._counter += 1

    def get_value(self):
        return self._value * 1.0 / self._counter
    
    def get_description(self):
        return self._description
    
    def get_unit(self):
        return self._unit

    def __str__(self):
        return self._formatter.format(self._description, self._value * 1.0 / self._counter, self._unit)


class TableStatistic:

    def __init__(self, titles, formatter = None):
        self._titles = titles
        self._values = []
        self._formatter = formatter

    def update(self, value):
        self._values.append(value)

    def __str__(self):

        if self._formatter is not None:
            return self._formatter(self._values)
        widths = [len(title) + 1 for title in self._titles]
        form_titles = "".join(["{:^" + str(w) + "}" for w in widths]) + "\n"
        form_values = "".join(["{:^" + str(w) + "}" for w in widths])
        return form_titles.format(*self._titles) + '\n'.join([form_values.format(*v) for v in self._values])

    
 # TODO: Derive on class that outputs to files.
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
        print(str(statistic))

        
class StatisticsCollection:
    """
        Singleton for handling statistics.

        NOTE: CURRENTLY STORES EVERYTHING ON RAM, UNTIL FLUSHED!
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