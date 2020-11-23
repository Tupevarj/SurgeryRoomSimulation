import logging
import sys
from enum import IntEnum

"""
    Logging Module

    Basic logging functionality with different log levels <LogLevel>.
    SimLogger expands basic Logger by prefixing logged messages with 
    simulation time.

    Basic usage (through static log method):
    SimLogger.log(<LogLevel>, <message>)

"""

class LogLevel(IntEnum):
    """
        Supported log level. For now, maps with standard logging 
        module levels for easy conversion.
    """
    DEBUG    = 10
    INFO     = 20
    WARNING  = 30
    ERROR    = 40
    CRITICAL = 50


class Logger(object):
    """
        Wrapper singleton class for Python standard logging.
    """
    
    __instance = None
    
    def __new__(cls, level, stdout=True, file=None, format = ('%(asctime)s %(levelname)5.5s - %(message)s', "%Y-%m-%d %H:%M:%S")):
        """
            Creates singleton instance (first call only).
        """
        if Logger.__instance is None:
            Logger.__instance = object.__new__(cls)
            Logger.__instance._log = logging.getLogger(__name__)
            Logger.__instance._log.setLevel(int(level))

            handlers = []
            stdout and handlers.append(logging.StreamHandler(sys.stdout))
            file is not None and handlers.append(logging.FileHandler(file))
            
            if len(handlers) != 0:
                logging.basicConfig(level=int(level), 
                                    force=True,
                                    format=format[0],
                                    datefmt=format[1],
                                    handlers=handlers)

            # Fast access lookup table for different logging methods:
            Logger.__instance._look_up_methods = { LogLevel.DEBUG:    logging.debug,
                                                   LogLevel.INFO:     logging.info,
                                                   LogLevel.WARNING:  logging.warning,
                                                   LogLevel.ERROR:    logging.error,
                                                   LogLevel.CRITICAL: logging.critical }
        return Logger.__instance


    @staticmethod
    def log(level, message):
        """
            Writes single <message> with log level <level> into log.
        """
        try:
            Logger.__instance._look_up_methods[level](message)
        except:
            pass


class SimLogger:
    """
        Adapter singleton class for Logger class that appends messages with simulation time.
    """

    __instance = None

    def __new__(cls, level, env, stdout=True, file=None):
        """
            Creates singleton instance (first call only).
        """
        if SimLogger.__instance is None:
            SimLogger.__instance = object.__new__(cls)
            SimLogger.__instance.__logger = Logger(level, stdout=stdout, file=file, format=('%(asctime)s %(levelname)5.5s - %(message)s', "%Y-%m-%d %H:%M:%S"))
            SimLogger.__instance.__env = env
        return SimLogger.__instance
        
    @staticmethod
    def log(level, message):
        """
            Writes single <message> (prefixed by simulation time) with log level <level> into log.
        """
        try:
            SimLogger.__instance.__logger.log(level, '({:.0f}) {}'.format(SimLogger.__instance.__env.now, message))
        except:
            pass
