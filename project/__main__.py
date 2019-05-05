import getopt
import os
import sys

from project import app

import warnings
warnings.filterwarnings(action='ignore',module='.*paramiko.*')


def cmd_helper():
    return """Usage: 
    app.py {OPTIONS}
    
    Options:
     
    -u <file>       Specify a user input file
        --user <file>
    -m <file>       (optional) Specify a staging module sequence
        --module <file>
    -r <job UUID>   Retrieve the result from a previously submitted job
        --retrieve <job UUID>
    """


def main(argv):
    try:
        opts, args = getopt.getopt(argv, "hu:m:r:", ["user=", "module=", "retrieve="])
    except getopt.GetoptError:
        print(cmd_helper())
        sys.exit(2)

    user_file = None
    module_file = None
    job_uuid = None

    for opt, arg in opts:
        if opt == '-h':
            print(cmd_helper())
            sys.exit()
        if opt in ("-u", "--user"):
            user_file = os.path.normpath(arg)
        if opt in ("-m", "--module"):
            module_file = os.path.normpath(arg)
        if opt in ("-r", "--retrieve"):
            job_uuid = str(arg)
    # TODO global error management
    if user_file is not None:
        if module_file is not None:
            # Launch staging w/ user input and staging module sequence
            app.run_with_module(user_file, module_file)
        else:
            # Launch staging on User Input only
            app.run(user_file)
    elif job_uuid is not None:
        app.retrieve(job_uuid)
    else:
        print(cmd_helper())


if __name__ == '__main__':
    main(sys.argv[1:])
