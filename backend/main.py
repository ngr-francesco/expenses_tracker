"""
This serves as a simulation to test the backend components
"""

from backend.sim.application import application

if __name__ == '__main__':
    app = application()
    app.run()