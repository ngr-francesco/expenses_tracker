from backend.utils.logging import get_logger
from backend.utils.time import get_timestamp_numerical, is_valid_timestamp
from backend.cls.object_with_id import ObjectWithId
from weakref import WeakSet
from copy import deepcopy

class Version:
    def __init__(self,state):
        self.state = state
        self.timestamp = get_timestamp_numerical()

class Saveable(ObjectWithId):
    # We track Saveable instances to allow save_all functionality
    _instances = WeakSet()
    def __init__(self):
        super().__init__()
        Saveable._instances.add(self)
        self._logger = get_logger(type(self).__name__)
        self._time_created = get_timestamp_numerical()
        self._version_history = [Version(self._capture_state())]
        self._current_version = -1
        self._just_undid_redid = False

    @property
    def logger(self):
        return self._logger
    @property
    def time_created(self):
        return self._time_created
    @time_created.setter
    def time_created(self,timestamp):
        if not is_valid_timestamp(timestamp):
            raise ValueError(f"Incompatible value for timestamp {timestamp}.")
        self._time_created = timestamp
    
    def takes_class_snapshot(func):
        def wrapper(self,*args,**kwargs):
            func(self,*args,**kwargs)
            self.logger.debug(f"Saving snapshot of class {type(self).__name__} to allow undo/redo.")
            self.save_version()
        return wrapper
    
    def affects_metadata(log_msg):
        def outer_wrapper(func):
            def inner_wrapper(self,*args,**kwargs):
                func(self,*args,**kwargs)
                msg = f"Saving {type(self).__name__} {self.name} after operation:" + log_msg
                self.logger.debug(msg)
                self.save_version()
                self.save_data()

            return inner_wrapper
        
        return outer_wrapper
    
    def save_version(self):
        self.logger.debug(self._just_undid_redid)
        # If we're coming after an undo/redo, we shouldn't re-save the snapshot
        if self._just_undid_redid:
            self.logger.debug("Skipping save_version after undo/redo")
            self._just_undid_redid = False
            return
        
        state = self._capture_state()
        self.logger.debug("State has changed, saving it.")
        # If we undid something and then changed stuff, reset the version history.
        if self._current_version < -1:
            self._version_history = self._version_history[:self._current_version+1]
        version = Version(state)
        self._version_history.append(version)

    def undo(self):
        if len(self._version_history) > 1:
            if abs(self._current_version) == len(self._version_history):
                self.logger.debug("Reached the end of version history.")
                return
            self.logger.debug("Undoing last changes.")
            self._current_version -= 1
            
            self._set_state()

    
    def redo(self):
        if len(self._version_history)> 1:
            if self._current_version == -1:
                self.logger.debug("Can't redo, reached the latest version.")
                return
            self.logger.debug("Redoing last changes.")
            self._current_version += 1
            self._set_state()
            

    @affects_metadata(log_msg="Undo/Redo")
    def _set_state(self):
        version = self._version_history[self._current_version]
        self._restore_state(version.state)
        self._just_undid_redid = True
    
    def _capture_state(self):
        self.logger.debug("Capturing state to add to undo/redo versions")
        snapshot = deepcopy(self,)
        if hasattr(snapshot,'members'):
            print(len(snapshot.members))
        return snapshot

    def _restore_state(self,state):
        for key,attr in vars(state).items():
            # TODO: this is not optimal, but it's a small overhead.
            if key.startswith('_'):
                continue
            setattr(self,key,attr)

    def save_data(self):
        raise NotImplementedError("method 'save_data' must be implemented in children of Saveable class")
    
    def load(self):
        raise NotImplementedError("method 'load' must be implemented in children of Saveable.")
            
