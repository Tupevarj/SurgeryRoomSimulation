
class ScalarStatistic:

    def __init__(self):
        self._counter = 0

    def increase(self):
        self._counter += 1


class TimeStampStatistic:

    def __init__(self):
        self._values = []

    def add(self, id, timestamp):
        self._values.append((id, timestamp))