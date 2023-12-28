from backend.utils.logging import get_logger
from backend.utils.time import get_timestamp_numerical

class Version:
    def __init__(self,state):
        self.state = state
        self.timestamp = get_timestamp_numerical()

class Saveable:
    def __init__(self):
        print(f"Initialized logger for class {type(self)}")
        self._logger = get_logger(type(self).__name__)
        self._time_created = get_timestamp_numerical()
        self._version_history = [Version(self._capture_state())]
        self._current_version = -1

    @property
    def logger(self):
        return self._logger
    @property
    def time_created(self):
        return self._time_created
    
    def affects_metadata(log_msg):
        def outer_wrapper(func):
            def inner_wrapper(self,*args,**kwargs):
                func(self,*args,**kwargs)
                msg = f"Saving {type(self).__name__} {self.name} after operation:" + log_msg
                self.save_version()
                self.logger.debug(msg)
                self.save_data()

            return inner_wrapper
        
        return outer_wrapper
    
    def save_version(self):
        state = self._capture_state()
        # If it's a state not present in previous versions
        if not state in self._version_history:
            # If we undid something and then changed stuff, reset the version history.
            if self._current_version < -1:
                self._version_history = self._version_history[:self._current_version+1]
            version = Version(self._capture_state())
            self._version_history.append(version)

    def undo(self):
        if len(self._version_history) > 1:
            if abs(self._current_version) == len(self._version_history):
                self.logger.debug("Reached the end of version history.")
                return
            self._current_version -= 1
            self._set_state()     
    
    def redo(self):
        if len(self._version_history)> 1:
            if self._current_version == -1:
                self.logger.debug("Can't redo, reached the latest version.")
                return
            self._current_version += 1
            self._set_state()

    @affects_metadata(log_msg="Undo/Redo")
    def _set_state(self):
        version = self._version_history[self._current_version]
        self._restore_state(version.state)
    
    def _capture_state(self):
        return {key:attr for key,attr in vars(self) if not key.startswith('_')}

    def _restore_state(self,state):
        for key,attr in state.items():
            setattr(self,key,attr)

    def save_data(self):
        raise NotImplementedError("method 'save_data' must be implemented in children of Saveable class")
            
