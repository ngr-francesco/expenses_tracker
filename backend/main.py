"""
This serves as a simulation to test the backend components
"""
from backend.utils.logging import Logger, LogLevel
from backend.sim.application import application

if __name__ == '__main__':
    Logger.set_log_level(LogLevel.DEBUG)
    app = application()
    app.run()