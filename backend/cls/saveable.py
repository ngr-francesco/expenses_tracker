from backend.utils.logging import get_logger

class Saveable:
    def __init__(self):
        print(f"Initialized logger for class {type(self)}")
        self.logger = get_logger(type(self).__name__)
    
    def affects_class_data(log_msg):
        def outer_wrapper(func):
            def inner_wrapper(self,*args,**kwargs):
                func(self,*args,**kwargs)
                msg = f"Saving {type(self).__name__} {self.name} after operation:" + log_msg
                self.logger.debug(msg)
                self.save_data()

            return inner_wrapper
        
        return outer_wrapper
    
    def save_data(self):
        raise NotImplementedError("method 'save_data' must be implemented in children of Saveable class")
            
