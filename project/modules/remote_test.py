import json
import os
import sys

if __name__ == "__main__":
    input_str = sys.argv[1]
    user_input = json.loads(input_str)

    with open('python_module_output.txt', 'w') as file:
        json.dump(user_input, file)

    print(json.dumps(user_input))
    exit(0)
