from . import runtime_info
import re

def parse(workload_manager, resources):
    if workload_manager == 'slurm':
        script = __slurm__(resources)
    else:
        raise Exception("Unknown workload manager: {}".format(workload_manager))
    return script


def parse_duration(param):
    regex = {'d': "\\d+(?=d)", 'h': "\\d+(?=h)", 'm': "\\d+(?=m)", 's': "\\d+(?=s)"}
    times = dict()

    for key, value in regex.items():
        re_res = re.search(value, param, re.IGNORECASE)
        try:
            times[key] = int(re_res.group())
        except AttributeError:
            times[key] = 0

    if times['h'] >= 24:
        times['d'] += times['h'] // 24
        times['h'] = times['h'] % 24
    if times['m'] >= 60:
        times['h'] += times['m'] // 60
        times['m'] = times['m'] % 60
    if times['s'] >= 60:
        times['m'] += times['s'] // 60
        times['s'] = times['s'] % 60

    if int(times['d']) > 0:
        return "{}-{:0=2d}:{:0=2d}:{:0=2d}".format(times['d'], times['h'], times['m'], times['s'])
    else:
        return "{:0=2d}:{:0=2d}:{:0=2d}".format(times['h'], times['m'], times['s'])


def parse_mem(param):
    re_res = re.findall("(\\d+)(?=G|M)(G|M)", param, re.IGNORECASE)
    mem = 0
    for res in re_res:
        if res[1] in ('G', 'g'):
            mem += int(res[0]) * 1024
        else:
            mem += int(res[0])
    return mem


def __slurm__(resources):
    # TODO handle if resources are empty
    # Based on the existing tool at http://www.ceci-hpc.be/scriptgen.html
    script = "#!/bin/bash\n"
    # Job Name == Job UUID
    script = script + "#SBATCH --job-name=" + runtime_info.user_input['job_uuid'] + "\n"

    # Job duration
    timestamp = parse_duration(resources['duration'])
    if 'nbr_jobs_in_array' in resources:
        script = script + "#SBATCH --time=" + timestamp + "\n"

    # Embarrassingly parallel jobs
    if 'nbr_jobs_in_array' in resources:
        script = script + "#SBATCH --array=1-" + str(resources['nbr_jobs_in_array']) + "\n"

    # Shared Memory / OpenMP jobs
    if 'nbr_threads_per_process' in resources:
        script = script + "#SBATCH --cpus-per-task=" + str(resources['nbr_threads_per_process']) + "\n"

    # Message passing / MPI jobs
    if 'nbr_processes' in resources:
        script = script + "#SBATCH --ntasks=" + str(resources['nbr_processes']) + "\n"
        if 'distribution' in resources:
            if resources['distribution'] == 'grouped':
                script = script + "#SBATCH --nodes=1\n"
            elif resources['distribution'] == 'scattered':
                script = script + "#SBATCH --ntasks-per-node=1\n"
            elif resources['distribution'] == 'distributed' and 'nbr_of_nodes' in resources:
                script = script + "#SBATCH --ntasks-per-node=1\n"
                script = script + "#SBATCH --nodes=" + str(resources['nbr_of_nodes']) + "\n"
    else:
        script = script + "#SBATCH --ntasks=1\n"

    # Memory
    memory = parse_mem(resources['memory_per_thread'])
    if 'nbr_jobs_in_array' in resources:
        script = script + "#SBATCH --mem-per-cpu=" + str(memory) + "\n"
        
    # Cluster specific values
    script = script + "#SBATCH --partition=" + runtime_info.user_input['destination_cluster']['partition'] + "\n"

    # Final values
    if 'nbr_threads_per_process' in resources:
        script = script + "export OMP_NUM_THREADS=" + str(resources['nbr_threads_per_process']) + "\n" \
                        + "export MKL_NUM_THREADS=" + str(resources['nbr_threads_per_process']) + "\n"
    if 'nbr_jobs_in_array' in resources:
        script = script + "echo 'Task ID: $SLURM_ARRAY_TASK_ID'\n"

    return script

