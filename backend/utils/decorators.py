from backend.utils.utils import reload_backend

def requires_reload(func):
    def wrapper(*args, **kwargs):
        func(*args,**kwargs)
        reload_backend()
    
    return wrapper

