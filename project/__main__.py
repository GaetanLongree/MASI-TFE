import os

from project import app
import sys, getopt

def cmd_helper():
    return """Usage: 
    app.py {OPTIONS}
    
    Options:
     
    -u <file>       Specify a user input file
        --user <file>
    -m <file>       (optional) Specify a staging module sequence
        --module <file>
    """

def main(argv):
    try:
        opts, args = getopt.getopt(argv, "hu:m:", ["user=", "module="])
    except getopt.GetoptError:
        print(cmd_helper())
        sys.exit(2)

    user_file = "E:\\git\\MASI-TFE\\project\\data\\user_input.yml"
    module_file = None

    for opt, arg in opts:
        if opt == '-h':
            print(cmd_helper())
            sys.exit()
        elif opt in ("-u", "--user"):
            user_file = arg
        elif opt in ("-m", "--module"):
            module_file = arg

    if user_file is not None:
        print("User input file: {}".format(user_file))
        # TODO Launch staging on User Input only

        app.run(user_file)
        if module_file is not None:
            print("Modules input file: {}".format(module_file))
            # TODO Launch staging w/ user input and staging module sequence
            app.run(user_file, module_file)
    else:
        print(cmd_helper())

if __name__ == '__main__':
    #app.run()
    main(sys.argv[1:])
