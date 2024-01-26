from backend.utils.const import default_data_dir
import os

class Settings:
    data_dir = default_data_dir


    def set_data_dir(path):
        if os.path.isdir(path):
            data_dir = os.path.join(path,'usr_data')

prefs = Settings
