from datetime import datetime

def get_timestamp_numerical():
    return datetime.now().strftime("%Y%m%d_%H%M%S_%f")

def get_timestamp_readable():
    return datetime.now().strftime("%Y-%m-%d %H:%M:S:%f")

def convert_timestamp_readable(timestamp):
    num_timestamp = datetime.strptime(timestamp,"%Y%m%d_%H%M%S_%f")
    return num_timestamp.strftime("%Y-%m-%d %H:%M:S:%f")
