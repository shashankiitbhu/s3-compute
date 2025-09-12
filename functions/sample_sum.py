def handler(payload):
    numbers = payload.get('numbers', [])
    if not isinstance(numbers, list):
        raise ValueError("numbers must be a list")
    
    return sum(numbers)