import json
import sys
import time

if __name__ == "__main__":
    input_str = sys.argv[1]
    user_input = json.loads(input_str)

    # simulate a very complex AI doing complex work...very quickly
    time.sleep(10) 

    if 'key1' in user_input['kwargs']:
        resources = {
            "duration": "30m",
            "memory_per_thread": user_input['kwargs']['key1'],
        }
    else:
        resources = {
            "duration": "30m",
            "memory_per_thread": "500M",
        }

    user_input['resources'] = resources

    print(json.dumps(user_input))
    exit(0)
