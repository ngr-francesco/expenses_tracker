class Singleton:
    _instances = {}

    def __new__(cls, *args, **kwargs):
        if cls not in cls._instances:
            # First get the instance from default python, then handle it.
            instance = super().__new__(cls)
            instance.__init__(*args, **kwargs)
            cls._instances[cls] = instance
        return cls._instances[cls]
    
    @staticmethod
    def has_instance(cls):
        return cls in cls._instances

    @staticmethod
    def get_instance(cls):
        if cls.has_instance(cls):
            return cls._instances[cls]