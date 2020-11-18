import logging
import sys
from enum import IntEnum


class LogLevel(IntEnum):
    """
        Supported log level. For now, maps with standard logging module 
        levels for easy conversion between these two.
    """
    DEBUG    = 10
    INFO     = 20
    WARNING  = 30
    ERROR    = 40
    CRITICAL = 50



class Logger:
    """
        Wrapper singleton class for python standard logging.
    """
    
    _instance = None

    class __Logger:
        """
            Nested class needed for singleton pattern.
        """
        def __init__(self, level, format, stdout=True, file=None):
            
            self._log = logging.getLogger(__name__)
            self._log.setLevel(int(level))

            # Use standard output:
            if stdout:
                log_handler = logging.StreamHandler(sys.stdout)
                log_format = logging.Formatter(*format)
                log_handler.setLevel(int(level))
                log_handler.setFormatter(log_format)
                self._log.addHandler(log_handler)

            if file is not None:
                # TODO: Add support to log into file
                pass

            self._look_up_methods = { LogLevel.DEBUG:    self._log.debug,
                                      LogLevel.INFO:     self._log.info,
                                      LogLevel.WARNING:  self._log.warning,
                                      LogLevel.ERROR:    self._log.error,
                                      LogLevel.CRITICAL: self._log.critical }

            
        def log(self, level, message):
            self._look_up_methods[level](message)


    def __init__(self, level, format = ('%(asctime)s %(levelname)5.5s - %(message)s', "%Y-%m-%d %H:%M:%S")):
        if Logger._instance is None:
            Logger._instance = self.__Logger(level, format)
        
    @staticmethod
    def log(level, message):
        try:
            Logger._instance.log(level, message)
        except:
            pass


class SimLogger:
    """
        Adapter class for Logger that adds simulation time into the messages.
    """
    _instance = None

    class __SimLogger:
        """
            Nested class needed for singleton pattern.
        """
        def __init__(self, level, env):
            Logger(level, format = ('%(asctime)s %(levelname)5.5s - %(message)s', "%Y-%m-%d %H:%M:%S"))
            self._env = env

            
        def log(self, level, message):
            try:
                Logger._instance.log(level, '({}) {}'.format(self._env.now, message))
            except:
                pass


    def __init__(self, level, env):
        if SimLogger._instance is None:
            SimLogger._instance = self.__SimLogger(level, env)
        
    @staticmethod
    def log(level, message):
        try:
            SimLogger._instance.log(level, message)
        except:
            pass