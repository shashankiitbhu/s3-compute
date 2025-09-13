import os
import json

def handler(payload):
    text = payload.get("text", "")
    return text.upper()

if __name__ == "__main__":
    payload = os.environ.get("PAYLOAD", "{}")
    data = json.loads(payload)
    print(handler(data))
