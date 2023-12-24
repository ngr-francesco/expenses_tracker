from enum import Enum
from datetime import datetime
import sys

class LogLevel(Enum):
    DIAGNOSTIC = 0
    DEBUG = 1
    INFO = 2
    WARNING = 3
    ERROR = 4
    CRITICAL = 5 

    def __le__(self,other):
        if isinstance(other,LogLevel):
            return self.value <= other.value

class Logger:

    # Static variable to hold the logging level.
    level = LogLevel.WARNING
    use_timestamps = False

    def __init__(self, name = None):
        """
        Initialize the logger in the DEBUG level.
        """
        self.name = name

    def log(self, level, message):
        """
        Log a message at the specified level.
        """
        if self.level <= level:
            sys.stdout.write(self.format_message(level, message))
            sys.stdout.flush()

    def format_message(self, level, message):
        """
        Format the message.
        """
        if Logger.use_timestamps:
            timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            return f"{timestamp} {level.name}\t{self.name}: {message}\n"
        return f"{level.name}\t{self.name}: {message}\n"

    def diagnostic(self, message):
        """
        Log a message at the DIAGNOSTIC level.
        """
        self.log(LogLevel.DIAGNOSTIC, message)
    
    def debug(self, message):
        """
        Log a message at the DEBUG level.
        """
        self.log(LogLevel.DEBUG, message)
    
    def info(self, message):
        """
        Log a message at the INFO level.
        """
        self.log(LogLevel.INFO, message)

    def warning(self, message):
        """
        Log a message at the WARNING level.
        """
        self.log(LogLevel.WARNING, message)
    
    def error(self, message):
        """
        Log a message at the ERROR level.
        """
        self.log(LogLevel.ERROR, message)
    
    def critical(self, message):
        """
        Log a message at the CRITICAL level.
        """
        self.log(LogLevel.CRITICAL, message)

    @staticmethod
    def set_log_level(level):
        """
        Finds any number of globally defined VL_Logger instances and sets their level.
        """
        if level in LogLevel:
            Logger.level = level
            sys.stdout.write(f"Set log level to {level.name}\n")
            sys.stdout.flush()
        else:
            raise ValueError(f"Invalid log level: {level}")
    @staticmethod
    def using_timestamps(use_timestamps:bool):
        if isinstance(use_timestamps,bool):
            Logger.use_timestamps = use_timestamps
        else:
            sys.stdout.write(f"WARN\t Incorrect type given to 'using_timestamps' method {type(use_timestamps)}.")
            sys.stdout.flush()


def get_logger(name):
    """
    Get a logger with the specified name.
    """
    logger =  Logger(name)
    return logger

