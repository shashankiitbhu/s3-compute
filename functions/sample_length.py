import os
import json

def handler(payload):
    data = payload.get("data", [])
    return len(data)

if __name__ == "__main__":
    payload = os.environ.get("PAYLOAD", "{}")
    data = json.loads(payload)
    print(handler(data))
