import getopt
import json
import sys
import traceback

from . import debug, setup, cleanup, execution, runtime_info, workload_manager, module_handler


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
            handler.from_dict(runtime_info.modules)

            # Preprocessing modules execution
            if runtime_info.modules is not None:
                preprocessing_output = handler.run('preprocessing', runtime_info.user_input)
                runtime_info.__update_input__(preprocessing_output['input'])
                runtime_info.__update_modules__(preprocessing_output['modules'])

            # Job Execution
            execution.run()
            # Wait for slurm to finish running the job
            terminated_successfully = execution.wait()

            if terminated_successfully and runtime_info.modules is not None:
            #if True and runtime_info.modules is not None:
                # Postprocessing modules execution
                postprocessing_output = handler.run('postprocessing', runtime_info.user_input)
                runtime_info.__update_input__(postprocessing_output['input'])
                runtime_info.__update_modules__(postprocessing_output['modules'])

            # Cleanup of local files
            #cleanup.run()
            cleanup.write_file_output(runtime_info.get_all())
            debug.log("\n" + json.dumps(runtime_info.get_all(), indent=6, sort_keys=True))
        except Exception as error:
            debug.log("Error caught: {}".format(error))
            debug.log("Traceback : {}".format(traceback.format_exc()))


if __name__ == '__main__':
    main(sys.argv[1:])
