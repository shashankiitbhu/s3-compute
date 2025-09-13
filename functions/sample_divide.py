import os
import json

def handler(payload):
    a = payload.get("a", 0)
    b = payload.get("b", 1)
    try:
        return a / b
    except ZeroDivisionError:
        return "Error: divide by zero"

if __name__ == "__main__":
    payload = os.environ.get("PAYLOAD", "{}")
    data = json.loads(payload)
    print(handler(data))
