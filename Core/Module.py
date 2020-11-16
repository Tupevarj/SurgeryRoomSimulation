from Logging import Logger, LogLevel


class ModuleBase(object):
    """
        Base class for different modules.
    """
    LOGGER = Logger(LogLevel.INFO)

    def __init__(self):
        pass


