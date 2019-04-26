import json
import sys

if __name__ == "__main__":
    input_str = sys.argv[1]
    user_input = json.loads(input_str)

    if 'key1' in user_input['kwargs'] and user_input['kwargs']['key1'] == 'value1':
        resources = {
            "nbr_jobs_in_array": 20,
            "duration": "5d4h32m1s",
            "nbr_processes": 10,
            "distribution": "distributed",
            "nbr_of_nodes": 4,
            "memory_per_thread": "2G",
            "nbr_threads_per_process": 2
        }
    else:
        resources = {
            "nbr_jobs_in_array": 5,
            "duration": "1d2h3m4s",
            "nbr_processes": 5,
            "distribution": "grouped",
            "memory_per_thread": "254M",
            "nbr_threads_per_process": 1
        }

    user_input['resources'] = resources

    print(json.dumps(user_input))
    exit(0)
