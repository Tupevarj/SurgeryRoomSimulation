from Core.Exceptions import SimulationException
from abc import ABCMeta, abstractmethod

"""

    Statistics Module

    Supports four different types of statistics:
    - ScalarStatistic:     Scalar statistics (single value increased by the <value> in update method).
    - CounterStatistic:    Counter statistics (counter increased by one in update method).
    - ScalarMeanStatistic: Mean scalar statistic (calculates means value of scalar).
    - TableStatistic:      Table statistics (with header and rows of values).

    Supports output to stdout (StatisticsWriterStdout) and to file (StatisticsWriterFile).

    Statistics can managed through StatisticsCollection singleton class.

"""


class ScalarStatisticBase(metaclass=ABCMeta):
    """
        Abstact base class for scalar statistics.
    """
    def __init__(self, description, unit, formatter):
        self._description = description
        self._unit = unit
        self._formatter = formatter
        self._value = 0
        
    def __str__(self):
        return self._formatter([self._description, self._value, self._unit])
    

class ScalarStatistic(ScalarStatisticBase):
    """
        Statistics for single scalar. Each update call increaes value by <value>.
    """
    def __init__(self, description, unit="", formatter = lambda values : "{:80} {} {}".format(*values)):
        super().__init__(description, unit, formatter)

    def update(self, value):
        self._value += value
    

class CounterStatistic(ScalarStatisticBase):
    """
        Counter statistic. Each update call increases value by one.
    """
    def __init__(self, description, unit="", formatter = lambda values : "{:80} {} {}".format(*values)):
        super().__init__(description, unit, formatter)

    def update(self):
        self._value += 1


class ScalarMeanStatistic(ScalarStatisticBase):
    """
        Mean value statistic.
    """

    def __init__(self, description, unit="", formatter = lambda values : "{:80} {:.2f} {}".format(*values)):
        super().__init__(description, unit, formatter)
        self._counter  = 0

    def update(self, value):
        self._value += value
        self._counter += 1

    def __str__(self):
        return self._formatter([self._description, self._value * 100.0 / self._counter, self._unit])


class TableStatistic:
    """
        Table statistics. Each update call adds single row to table.
    """
    def __init__(self, titles, formatter = None):
        self._titles = titles
        self._values = []
        self._formatter = self._table_to_csv if formatter is None else formatter

    def update(self, value):
        self._values.append(value)

    def __str__(self):
        return self._formatter(self._values)

    def _table_to_string(self, values):
        widths = [max(len(title) + 1, 8) for title in self._titles]
        return ("".join(["{:^" + str(w) + "}" for w in widths]) + "\n").format(*self._titles) + '\n'.join([("".join(["{:^" + str(w) + "}" for w in widths])).format(*v) for v in self._values])

    def _table_to_csv(self, values):
        return "SEP=,\n" +(",".join(["{}" for t in self._titles]) + "\n").format(*self._titles) + '\n'.join([(",".join(["{}" for t in self._titles])).format(*v) for v in self._values])
        
    
class StatisticsWriter(metaclass=ABCMeta):
    """
        Statistic output interface. TODO: Derive on that outputs to file.
    """
    def __init__(self):
        pass
    
    @abstractmethod
    def output_statistics(self, statistic, *args):
        pass


class StatisticsWriterStdout(StatisticsWriter):
    """
        Statistic output to stdout.
    """
    def __init__(self):
        pass
    
    def output_statistics(self, statistics):
        for stat in statistics:
            print(str(stat))

        
class StatisticsWriterFile(StatisticsWriter):
    """
        Statistic output to file.
    """
    def __init__(self):
        pass
    
    def output_statistics(self, statistics, path):
        with path.open('w') as file:
            for stat in statistics:
                file.write(str(stat) + "\n")


class StatisticsCollection:
    """
        Singleton for storing statistics.
    """
    __instance = None
    
    def __new__(cls):
        """
            Creates singleton instance (first call only).
        """
        if StatisticsCollection.__instance is None:
            StatisticsCollection.__instance = object.__new__(cls)
            StatisticsCollection.__instance.__statistics = dict()
        return StatisticsCollection.__instance


    @staticmethod
    def add_statistic(name, statistic):
        """
            Adds new statistic to the collection.
        """
        if name in StatisticsCollection.__instance.__statistics:
            raise SimulationException("Statistics '{}' already exists.".format(name))
        StatisticsCollection.__instance.__statistics[name] = statistic
        

    @staticmethod
    def update_statistic(name, *args):
        """
            Adds data to previously created statistic.
        """
        if name not in StatisticsCollection.__instance.__statistics:
            raise SimulationException("Statistics '{}' does not exist.".format(name))
        StatisticsCollection.__instance.__statistics[name].update(*args)


    @staticmethod
    def output_statistic(names, output, *args):
        """
            Outputs statistic(s). Depending on <output>, can output to stdout or file.
        """
        if isinstance(names, str):
            names = {names}
       
        if not StatisticsCollection.__instance.__statistics.keys() >= names:
            raise SimulationException("Statistics '{}' does not exist.".format(names))
        output.output_statistics([StatisticsCollection.__instance.__statistics[name] for name in names], *args)
