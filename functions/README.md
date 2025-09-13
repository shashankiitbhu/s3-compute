# Sample Functions for S3-for-Compute

This folder contains Python modules for testing the compute platform.  
Each module supports both legacy import-based and Docker script execution.

## Usage

- Upload any file via the UI or API.
- Payload should be a JSON object matching the function's requirements.

## Functions

- sample_add: `{"a": 1, "b": 2}`
- sample_subtract: `{"a": 5, "b": 3}`
- sample_multiply: `{"a": 2, "b": 4}`
- sample_divide: `{"a": 10, "b": 2}`
- sample_power: `{"base": 2, "exp": 3}`
- sample_reverse: `{"text": "hello"}`
- sample_upper: `{"text": "hello"}`
- sample_length: `{"data": [1,2,3]}`
- sample_sleep: `{"seconds": 2}`
- sample_sum: `{"numbers": [1,2,3,4,5]}`
