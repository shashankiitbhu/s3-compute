import os
import json

def handler(payload):
    base = payload.get("base", 0)
    exp = payload.get("exp", 1)
    return base ** exp

if __name__ == "__main__":
    payload = os.environ.get("PAYLOAD", "{}")
    data = json.loads(payload)
    print(handler(data))
