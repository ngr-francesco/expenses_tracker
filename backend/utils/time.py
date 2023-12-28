from datetime import datetime
import re

def get_timestamp_numerical():
    return datetime.now().strftime("%Y%m%d_%H%M%S_%f")

def get_timestamp_readable():
    return datetime.now().strftime("%Y-%m-%d %H:%M:S:%f")

def convert_timestamp_readable(timestamp):
    num_timestamp = datetime.strptime(timestamp,"%Y%m%d_%H%M%S_%f")
    return num_timestamp.strftime("%Y-%m-%d %H:%M:S:%f")

def is_valid_timestamp(timestamp_str):
    timestamp_format = r'\d{8}_\d{6}_\d{6}'  # Adjust the pattern based on your expected format
    return bool(re.fullmatch(timestamp_format, timestamp_str))