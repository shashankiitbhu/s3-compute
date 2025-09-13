import os
import json

payload = os.environ.get("PAYLOAD", "{}")
data = json.loads(payload)
numbers = data.get("numbers", [])
print(sum(numbers))