import shlex
import subprocess
import time

import numpy

from . import runtime_info, debug
import re


def get(workload_manager):
    if workload_manager == 'slurm':
        return Slurm
    else:
        raise Exception("Unknown workload manager: {}".format(workload_manager))


def parse(workload_manager, destination_cluster, resources, commands):
    return get(workload_manager).create_script(destination_cluster, resources, commands)


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


class Slurm(object):
    TERMINATED_STATUSES = ("BOOT_FAIL", "CANCELLED", "COMPLETED", "DEADLINE", "FAILED", "NODE_FAIL",
                           "OUT_OF_MEMORY", "PREEMPTED", "TIMEOUT")
    TERMINATED_SUCCESSFULLY_STATUSES = ("COMPLETED",)
    WAITING_STATUSES = ("PENDING", "CONFIGURING")
    RUNNING_STATUSES = ("RUNNING",)
    EVENT_STATUSES = ("COMPLETING", "RESV_DEL_HOLD", "REQUEUE_FED", "REQUEUE_HOLD", "REQUEUED",
                      "RESIZING", "REVOKED", "SIGNALING", "SPECIAL_EXIT", "STAGE_OUT", "STOPPED", "SUSPENDED")

    @staticmethod
    def get_cluster_resources():
        process = subprocess.Popen(shlex.split('sinfo -N --format="%N;%a;%b;%c;%z;%O;%m;%e"'),
                                   stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        output, err = process.communicate()
        return_code = process.returncode

        if return_code == 0:
            output = output.split('\n')
            cluster = dict()
            nodes = dict()
            for row, i in zip(output, range(0, len(output))):
                output[i] = row.split(';')

            for i in range(1, len(output[0])):
                for row in output[1:-1]:
                    try:
                        nodes[row[0]][output[0][i]] = row[i]
                    except KeyError:
                        nodes[row[0]] = dict()
                        nodes[row[0]][output[0][i]] = row[i]

            # Get sum of all nodes numerical nodes for the entire cluster
            for key in nodes.keys():
                if nodes[key]["AVAIL"] == "up":
                    for subkey in nodes[key].keys():
                        if subkey is not "AVAIL":
                            try:
                                cluster[subkey] = cluster[subkey] + float(nodes[key][subkey])
                            except KeyError:
                                cluster[subkey] = 0
                                try:
                                    cluster[subkey] = cluster[subkey] + float(nodes[key][subkey])
                                except ValueError:
                                    del cluster[subkey]
                            except ValueError:
                                pass
                    try:
                        cluster['AVAIL'] = cluster['AVAIL'] + 1
                    except KeyError:
                        cluster['AVAIL'] = 0
                        cluster['AVAIL'] = cluster['AVAIL'] + 1

            cluster['CPU_LOAD'] = cluster['CPU_LOAD'] / len(nodes)
            cluster['TOTAL_NODES'] = len(nodes)
            cluster['NODES'] = nodes
            cluster['TIMESTAMP'] = time.time()

            return cluster
        else:
            debug.log("ERROR: Gathering Slurm cluster stats returned non-zero error code.")

    @staticmethod
    def get_job_status():
        # process = subprocess.Popen(shlex.split('squeue --name=' + runtime_info.job_uuid + \
        #                                        ' --format="%j;%A;%D;%C;%m;%l;%N;%o;%T;%r"'),
        #                            stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

        process = subprocess.Popen(shlex.split('sacct --name=' + runtime_info.job_uuid + \
                                               ' --format=JobName,JobID,NNodes,NodeList,AllocTRES,ReqTRES,CPUTime,'
                                               'Elapsed,NCPUS,WorkDir,State,ExitCode --parsable2'),
                                   stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        output, err = process.communicate()
        return_code = process.returncode

        if return_code == 0:
            output = output.split('\n')
            job_submission = dict()
            for row, i in zip(output, range(0, len(output))):
                output[i] = row.split('|')

            for i in range(1, len(output[0])):
                for row in output[1:-1]:
                    if row[0] is not "":
                        try:
                            job_submission[row[0]][output[0][i]].append(row[i])
                        except KeyError:
                            if row[0] not in job_submission:
                                job_submission[row[0]] = dict()
                            if output[0][i] not in job_submission[row[0]]:
                                job_submission[row[0]][output[0][i]] = list()
                                job_submission[row[0]][output[0][i]].append(row[i])

            return job_submission

    @staticmethod
    def get_job_states(job_status):
        try:
            return job_status[runtime_info.job_uuid]['State']
        except KeyError:
            return {}  # TODO if empty --> get info from sacct

    @staticmethod
    def create_script(destination_cluster, resources, commands):
        # TODO handle if resources are empty
        # Based on the existing tool at http://www.ceci-hpc.be/scriptgen.html
        script = "#!/bin/bash\n"
        # Job Name == Job UUID
        script += "#SBATCH --job-name=" + runtime_info.job_uuid + "\n"

        # Job duration
        timestamp = parse_duration(resources['duration'])
        if 'duration' in resources:
            script += "#SBATCH --time=" + timestamp + "\n"

        # Embarrassingly parallel jobs
        if 'nbr_jobs_in_array' in resources:
            script += "#SBATCH --array=1-" + str(resources['nbr_jobs_in_array']) + "\n"

        # Shared Memory / OpenMP jobs
        if 'nbr_threads_per_process' in resources:
            script += "#SBATCH --cpus-per-task=" + str(resources['nbr_threads_per_process']) + "\n"

        # Message passing / MPI jobs
        if 'nbr_processes' in resources:
            script += "#SBATCH --ntasks=" + str(resources['nbr_processes']) + "\n"
            if 'distribution' in resources:
                if resources['distribution'] == 'grouped':
                    script += "#SBATCH --nodes=1\n"
                elif resources['distribution'] == 'scattered':
                    script += "#SBATCH --ntasks-per-node=1\n"
                elif resources['distribution'] == 'distributed' and 'nbr_of_nodes' in resources:
                    script += "#SBATCH --ntasks-per-node=1\n"
                    script += "#SBATCH --nodes=" + str(resources['nbr_of_nodes']) + "\n"
        else:
            script += "#SBATCH --ntasks=1\n"

        # Memory
        memory = parse_mem(resources['memory_per_thread'])
        if 'memory_per_thread' in resources:
            script += "#SBATCH --mem-per-cpu=" + str(memory) + "\n"

        # Cluster specific values
        if 'partition' in destination_cluster:
            script += "#SBATCH --partition=" + destination_cluster['partition'] + "\n"

        script += "\n"

        # Final values
        if 'nbr_threads_per_process' in resources:
            script += "export OMP_NUM_THREADS=" + str(resources['nbr_threads_per_process']) + "\n" \
                      + "export MKL_NUM_THREADS=" + str(resources['nbr_threads_per_process']) + "\n"
        if 'nbr_jobs_in_array' in resources:
            script += "echo 'Task ID: $SLURM_ARRAY_TASK_ID'\n"

        script += "\n"

        # Commands
        if len(commands) > 0:
            if isinstance(commands, str):
                script += commands + "\n"
            elif isinstance(commands, list):
                for command in commands:
                    script += command + "\n"

        return script
