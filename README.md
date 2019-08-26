# Master's Thesis - "Automated Job Submission Management for Grid Computing"

This repository contains the prototype for my Master's thesis realized at Henallux 
for the [Master's in IT Systems Architecture](https://www.henallux.be/architecture-des-systemes-informatiques-master).

The complete Master's Thesis, titled **Automated Job Submission Management for Grid Computing**, can be found [here](https://www.longree.be/data/tfe.pdf).

## Description

The objective of this thesis is to create an architecture to aid in the submission,
monitoring and retrieval of scientific jobs submitted to various HPC clusters regrouped
within the [CECI](http://www.ceci-hpc.be/).

This proof of concept is a partial implementation of some of the features proposed within my
thesis, applied to a command line utility tool.

## Requirements

This prototype leverages information leveraged within a database accessed entirely through 
a REST API. Both are self-hosted due to the limited extend of this proof of concept, however
below you will find the information required if you wish to reproduce the infrastructure to run
this proof of concept. 

### Database

The database used is MongoDB, however any form of document database should work if you wish to
adapt the API's code. Same is applicable for any type of database, although more work will be
required to adapt the code.

For simplicity, the database is not protected by any authentication mechanisms, mainly because
it was accessed only by the API as it's backend, while the API's frontend is protected.
For this prototype, the MongoDB was hosted on a Ubuntu Server in a Docker container using the 
following command:

`docker run -d -p 27017:27017 -v ~/mongodb:/data/db mongo`

A database named `masi_tfe` was used with the following collections/tables:
* **clusters**: containing an inventory of the clusters (in this project, those present in the CECI)
* **jobs**: where each job submission was submitted

All of the database access code for the API server is located in the `api_srv/dao` folder, with a 
`config.ini` file containing the database access values.

#### Schema 

##### clusters

The following is an example item for the Lemaitre3 cluster hosted at the "Université catholique 
de Louvain".

```json
{ 
  "_id" : ObjectId("5ccd9ade865e7214bb340e7a"), 
  "name" : "lemaitre3", 
  "hostname" : "lemaitre3.cism.ucl.ac.be", 
  "port" : 22, 
  "workload_manager" : "slurm", 
  "preferred_jobs" : [ "mpi" ], 
  "partition" : "batch", 
  "status" : {}
}
```

The `name` variable is used as a more user-friendly identifier for the user-input. The 
`workload_ manager` is by `workload_manager.py` in order to dynamically know how to interact 
with the cluster's workload manager. In the case of this prototype, Slurm was the only 
load manager to interact with. The `preferred_jobs` is used to indicate which type of jobs the
cluster is best suited for. The possible values for this field used in this prototype are 
`mpi`, `serial` and `smp`. These values are used upon submission to find alternative 
destination clusters if the user's original target is not available/reachable. The 
`partition` field is a data proper to Slurm scripting and the CECI clusters (variable 
depending on the cluster).

The `status` value is used to store resource information regarding the cluster as a whole as well
as its independent nodes. This value is update by the **wrapper** module upon execution on the
destination cluster (see full thesis for more details).

##### jobs

The following is an example of job submission after its completion.

```json
{
  "_id" : ObjectId("5ccf3e094a80d939aee76f29"),
  "job_uuid" : "503d3f77-a21b-4e52-86c4-eec0f0cd9c16",
  "user_input" : { 
    "username" : "glongree", 
    "requirements" : [ "chmod +x job" ], 
    "user_mail" : "gaetanlongree@gmail.com", 
    "job" : "https://github.com/GaetanLongree/test.git", 
    "destination_cluster" : "lemaitre3", 
    "kwargs" : { 
      "key1" : "value1"
    }, 
    "output" : [ "result.txt" ], 
    "execution" : [ "srun ./job" ], 
    "resources" : { 
      "duration" : "10m", 
      "memory_per_thread" : "100M"
    }
  }, 
  "destination_cluster" : { 
    "partition" : "batch", 
    "name" : "lemaitre3", 
    "hostname" : "lemaitre3.cism.ucl.ac.be", 
    "preferred_jobs" : [ "mpi" ], 
    "workload_manager" : "slurm", 
    "port" : 22
  }, 
  "modules" : null, 
  "online_job_file" : true, 
  "tar_file" : null, 
  "job_directory" : "/home/users/g/l/glongree/503d3f77-a21b-4e52-86c4-eec0f0cd9c16/", 
  "job_status" : { 
    "ReqTRES" : [ "cpu=1,mem=100M,node=1" ], 
    "WorkDir" : [ "/home/users/g/l/glongree/503d3f77-a21b-4e52-86c4-eec0f0cd9c16/test" ], 
    "NodeList" : [ "lm3-w080" ], 
    "NCPUS" : [ "1" ], 
    "CPUTime" : [ "00:00:17" ], 
    "JobID" : [ "67873032" ], 
    "State" : [ "COMPLETED" ], 
    "NNodes" : [ "1" ], 
    "AllocTRES" : [ "cpu=1,mem=100M,node=1,billing=1" ], 
    "Elapsed" : [ "00:08:20" ], 
    "ExitCode" : [ "0:0" ]
  }, 
  "working_directory" : "/home/users/g/l/glongree/503d3f77-a21b-4e52-86c4-eec0f0cd9c16/test"
}
```

The `job_uuid` is the value generated upon submission and used by the user to track the job status.
The `user_input` values corresponds to the data submitted by the user (explained in later section).
The `destination_cluster` contains the values of the cluster on which the job is being ran. The
`modules` field contains information relating to the external modules executed, at which stage
and what were their output (described later as well). The `online_job_file` is used to know whether
the job submitted is purely stored online or if it is a local file that needs to be transferred to
the cluster. The `tar_file` is used in case the job files are local but are multiple and are part 
of a directory (the folder is compressed into a TAR file to optimize transfers). The `job_directory`
and `working_directory` represent, respectively, the base location of the job folder and the 
location where the job proper is being ran by the workload manager. The `job_status` is the 
information gathered regarding the job and is obtained by the `workload_manager.py` module based
on the underlying workload manager used by the cluster (again, Slurm in this prototype's use case).

### REST API

The rest API is self-hosted at my own domain, and is also ran on an Ubuntu server in a docker 
container. This docker container is built from the `Dockerfile` located in the root of this 
repository. Due to the nature of Flask and the IP binding, the commands to build and run the 
container are done on the using the host's network. While this is not a recommended practice, 
the API was very accessory to the prototype, hence it did not require to operate under the best 
practices, it merely required to be working.

The commands to build and run the container are as follows:

```
docker build --no-cache --network=host -t tfe_api .
docker run -p 7676:7676 --network host -d --name tfe_api_srv tfe_api
```

The Flask server did not use an SSL certificate, as it was behind a reverse proxy using HTTPS
transparently. The API server does use a simple Basic Authentication merely as basic protection 
since the API was publicly accessible. To change the authentication username and password,
edit the values in `api_srv/tools/authenticator.py`.

The endpoints used are as follows:

| Endpoint | Method | Details |
| --- |:---:| --- |
| **/clusters** | GET | Used to get all the clusters and their details. |
| **/clusters** | PUT | Updates the status of a cluster. Requires the name of the cluster in the payload to identify the target cluster, and status field containing the entire values to update. |
| **/jobs/<job_id>** | GET | Return the entire values stored for a given job UUID. |
| **/jobs/<job_id>** | POST | Used to create a new job. |
| **/jobs/<job_id>** | PUT | Used to update a current job ID. The payload's content will update the existing fields without overwriting the entire job. |
| **/jobs/<job_id>/state** | GET | Returns an array of the job's current state (array is used for parallel jobs). |
| **/jobs/<job_id>/state** | PUT | Used to instruct the API server to send a mail to the job's owner regarding an update in the job's current state. |
| **/jobs/<job_id>/notify** | PUT | Used to instruct the API server to send a mail to the job's owner regarding an error that has occurred along with the error message. |

The mail service used for the `/jobs/<job_id>/state` and the `/jobs/<job_id>/notify` endpoints
can be modified to use another mail provider by editing the values in the `api_svr/tools/mailer.py`
file.

For the service and the prototype to work you must edit some values in three separate files:
* In the API server files:
    * Edit the `api_srv/__main__.py` file to change the **SERVER_IP** and **SERVER_PORT** values
* In the Project files:
    * Edit the `project/tools/api_handler.py` file to change the **URI** and **AUTH** values
    * Edit the `project/tools/wrapper/api_communicator.py` file to change the **URI** and **AUTH** values  

## Usage

There are three possible use cases to use this prototype:
* Submitting a job
* Submitting a job along with external modules to execute
* Retrieving a already submitted job

To submit a job, from this repository's root folder, run the following command:

`python -m project -u <path/to/user/input/file>`

To submit a job along with a list of modules to execute (from this repository's root folder still):

`python -m project -u <path/to/user/input/file> -m <path/to/modules/file>`

Depending on the user input files, you may be given various warnings about required or optional 
values missing from the input file.

You will also be asked to enter the passphrase for the private key file you have provided before
the connection is made.

Lastly, if the job submission was successful, you will be given a UUID specific to your job.
If the API server and `mailer.py` modules have been correctly configured, you will also receive 
emails whenever there is a change in your job's running state.

To retrieve a job, using the UUID given at submission, use the following command (from this
repository's root folder):

`python -m project -r <uuid>`

The following sections describe the **user input** and **modules specification** files along with 
some specifics.

### User Input

The user input file is a YAML file, a sample file can be found in the root of this repository,
with the content presented and explained below.

```yaml
username: jdoe
private_key: "path_to_key"
passphrase: "private_key_passphrase"
user_mail: johndoe@mail.com
destination_cluster: lemaitre3
requirements:
  - "chmod +x job"
job: https://github.com/GaetanLongree/test.git
compilation:
  - "gcc job.c"
execution:
  - "srun ./job"
output:
  - "result.txt"
resources:
  nbr_jobs_in_array: 15
  duration: 1d2h30m
  nbr_processes: 5
  nbr_threads_per_process: 2
  memory_per_thread: 2625M
  distribution: distributed
    # grouped | scattered | distributed
  #if 'distributed' only
  nbr_of_nodes: 4
kwargs:
  key1: value1
```

The table below reprises the 

| Key | Value |
| --- | --- |
| username | Your username used on the CECI clusters. |
| private_key | Path to the private key file used to authenticate on the CECI clusters |
| passphrase | *(optional)* The passphrase for the private key file. If not provided, will be asked in the command line. |
| user_mail | The email address where the mail notifier will send job state updates and notifications. |
| destination_cluster | The name of the cluster to which to submit the job. If the cluster is not reachable, the program will propose other reachable clusters that present the same preferred jobs as the cluster originally indicated. |
| requirements | *(optional)* A list of commands that will be executed as is on the destination cluster. This can be used to install additional packages from source for example. |
| job | Can be a file, a directory or a Git URL. If a file is given, it will be transferred to the destination cluster using SFTP. If a directoyr is given, it will be compressed in a TAR archive before being transferred, and will be unpacked before execution. If a git repository is given, it will be clones (recursively) and the working directory will be automatically set to the cloned repository's folder. |
| compilation | *(optional)* If the job requires compilation prior to execution, enter the full command to run. Can be a single command, or a list of commands. |
| execution | The list of commands to enter within the Slurm script. Commands must be complete and include the `srun` directive if necessary. |
| output | A single value or a list of values of the files where the job's result will be stored. This value is used by the retrieval function to pull the output of the job after execution. |
| resources | *(optional)* The resources to use for the job. These values are translated into the Slurm script. See note below. |
| kwargs | *(optional)* A list of keyword arguments that can be used by external modules. The entire user input will be passed to each external module in order for them to make use of this information if needed. |

##### Resources values

The resources are not mandatory, as it is assumed that the user may make use of external modules
to determine the resources.

The resource values such as `duration` and `memory_per_thread` are translated from human
readable form into the workload managers expected values. The supported values are as follows are
`d`, `h`, `m` and `s` for the `duration`, and `G` and `M` for the `memory_per_thread`.

Regarding the `distribution` key, this can take 3 values:
* `grouped`
* `scattered`
* `distributed`

If the value is `distributed`, a `nbr_of_nodes` is required to tell the Slurm workload manager how
to distribute the job across the nodes. 

### External Modules

This project is based around the ability to execute external modules in addition to submitting job.
The modules are executed at three stages: **staging**, executed locally before connecting to the
cluster, **preprocessing**, after connecting to the cluster and before the job submission on the
cluster, and finally **postprocessing**, after the job has executed and completed successfully.

The modular execution supports any language as long as the compiler and/or interpreter is present.
Despite this fact, it is not impossible to execute modules where the interpreter is not present,
but it will require manual installing through the `requirements` section of the user input values.

A sample `modules_sample.yml` file is present in the root folder of this repository, with the
content presented and explained below.

```yaml
staging:
  1:
    module: test.c
    compilation: gcc -o test test.c
    execution: ./test
  2:
    module: resource_estimator.py
    execution: python resource_estimator.py
preprocessing:
  1:
    module: remote_test.c
    compilation: gcc -o remote_test remote_test.c
    execution: ./remote_test
  2:
    module: resource_estimator.py
    execution: python resource_estimator.py
postprocessing:
  1:
    module: test.c
    compilation: gcc -o test test.c
    execution: ./test
  2:
    module: remote_test.py
    execution: python remote_test.py
```

The top three stages are represented, each containing numbered key/value pairs of objects. These 
numbered keys act as indexes to determine the order of execution.

The `module` directive is used to instruct which module is to be executed, and therefore transferred
to the destination cluster. The project will look for modules in the `project/modules` folder, 
which is where you must place the module you which to use.

The `compilation` directive is *optinal* and is used if the module requires compilation. This command must be 
entered exactly as it would be entered on the destination cluster, including the name of module 
itself. This was done in order to account for future-proofing any modules with specific compilation
commands.(Note: the original idea was to omit the need to specify the module file.)

The `execution` directive is used to specify how to execute the module. The command must be written
exactly as it is to be executed on the remote system.

#### Modules' Input and Output

When a module is executed, it will be automatically be passed as argument the user input key/pair 
structure as it is at this stage of the execution.

By the end of the modules execution, it must output through the regular STDOUT the same key/pair
structure, either modified internally or unmodified if it has not been altered.

This mechanism is implemented in order for the modules to have direct interaction with the user 
input and potentially alter them, while allowing subsequent modules to have access to the
information performed. 



