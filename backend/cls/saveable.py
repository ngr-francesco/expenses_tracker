from backend.utils.logging import get_logger

class Saveable:
    def ___init__(self):
        self.logger = get_logger(type(self).__name__)
    
    def affects_class_data(self,log_msg):
        def outer_wrapper(func):
            def inner_wrapper(*args,**kwargs):
                func(*args,**kwargs)
                log_msg = f"Saving {type(self).__name__} {self.name} after operation:" + log_msg
                self.logger.debug(log_msg)
                self.save_data()

            return inner_wrapper
        
        return outer_wrapper
    
    def save_data(self):
        raise NotImplementedError("method 'save_data' must be implemented in children of Saveable class")
            
