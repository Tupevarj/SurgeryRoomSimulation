from Core.Exceptions import SimulationException

class ScalarStatistic:

    def __init__(self):
        self._counter = 0

    def update(self):
        self._counter += 1


class TimeStampStatistic:

    def __init__(self):
        self._values = []

    def update(self, id, timestamp):
        self._values.append((id, timestamp))


class StatisticsOut:
    # One for file, one for stdout
    pass

        
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
        pass