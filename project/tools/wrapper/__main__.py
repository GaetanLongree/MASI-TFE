import getopt
import sys
import traceback

from . import debug, setup, cleanup, execution, runtime_info ,module_handler


def main(argv):
    try:
        opts, args = getopt.getopt(argv, "i:")
    except getopt.GetoptError:
        debug.log("Error in the command parameters")
        sys.exit(2)

    input_file = None

    for opt, arg in opts:
        if opt == '-i':
            input_file = arg

    if input_file is not None:
        try:
            # Setup stage
            setup.run(input_file)

            # Module handling setup
            handler = module_handler.ModuleHandler()
            handler.from_dict(runtime_info.user_input['modules'])

            # Preprocessing modules execution
            preprocessing_output = handler.run('preprocessing', runtime_info.user_input)
            debug.log(preprocessing_output)
            runtime_info.__update_input__(preprocessing_output)

            # Job Execution
            execution.run()
            # TODO wait for slurm to finish running the job

            # Postprocessing modules execution
            postprocessing_output = handler.run('postprocessing', runtime_info.user_input)
            debug.log(postprocessing_output)
            runtime_info.__update_input__(postprocessing_output)

            # Cleanup of local files
            #cleanup.run()
            cleanup.write_file_output(runtime_info.user_input)
        except Exception as error:
            debug.log("Error caught: {}".format(error))
            debug.log("Traceback : {}".format(traceback.format_exc()))


if __name__ == '__main__':
    main(sys.argv[1:])
