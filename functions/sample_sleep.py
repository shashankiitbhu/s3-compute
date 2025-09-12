import time

def handler(payload):
    seconds = payload.get('seconds', 1)
    if not isinstance(seconds, (int, float)) or seconds < 0:
        raise ValueError("seconds must be a non-negative number")
    
    time.sleep(seconds)
    return "done"