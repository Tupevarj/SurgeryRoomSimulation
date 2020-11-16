import logging
import sys
from enum import IntEnum


class LogLevel(IntEnum):
    """
        Supported log level. For now, maps with standard logging module 
        levels for easy conversion between these two.
    """
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
        def __init__(self, level, stdout=True, file=None):
            
            self._log = logging.getLogger(__name__)
            self._log.setLevel(int(level))

            # Use standard output:
            
            if stdout:
                log_handler = logging.StreamHandler(sys.stdout)
                log_format = logging.Formatter('%(asctime)s %(levelname)s - %(message)s', "%Y-%m-%d %H:%M:%S")
                log_handler.setLevel(int(level))
                log_handler.setFormatter(log_format)
                self._log.addHandler(log_handler)

            if file is not None:
                # TODO: Add support to log into file
                pass

            self._look_up_methods = { LogLevel.INFO:     self._log.info,
                                      LogLevel.WARNING:  self._log.warning,
                                      LogLevel.ERROR:    self._log.error,
                                      LogLevel.CRITICAL: self._log.critical }

            
        def log(self, level, message):
            self._look_up_methods[level](message)


    def __init__(self, level):
        if Logger._instance is None:
            Logger._instance = self.__Logger(level)
        
    @staticmethod
    def log(level, message):
        try:
            Logger._instance.log(level, message)
        except:
            pass

