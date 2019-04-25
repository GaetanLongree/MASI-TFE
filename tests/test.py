import json
import os
import tarfile

if __name__ == '__main__':
    test = {
        'key1': 'value1',
        'key2': 'value2'
    }
    with open('input.json', 'w') as file:
        json.dump(test, file)
