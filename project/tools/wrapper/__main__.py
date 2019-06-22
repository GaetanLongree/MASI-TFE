import getopt
import sys
import traceback

from . import debug, setup, cleanup, execution, runtime_info, workload_manager, module_handler, api_communicator


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

            #  modules execution
            if runtime_info.modules is not None \
                    and 'preprocessing' in runtime_info.modules:
                try:
                    preprocessing_output = handler.run('preprocessing', runtime_info.user_input)
                    runtime_info.__update_input__(preprocessing_output['input'])
                    runtime_info.__update_modules__(preprocessing_output['modules'])
                except Exception as err_msg:
                    debug.log(err_msg)
                    api_communicator.notify_client(err_msg)

            # Job Execution
            execution.run()
            # Wait for slurm to finish running the job
            terminated_successfully = execution.wait()

            if terminated_successfully \
                    and runtime_info.modules is not None \
                    and 'postprocessing' in runtime_info.modules:
                # Postprocessing modules execution
                try:
                    postprocessing_output = handler.run('postprocessing', runtime_info.user_input)
                    runtime_info.__update_input__(postprocessing_output['input'])
                    runtime_info.__update_modules__(postprocessing_output['modules'])
                except Exception as err_msg:
                    debug.log(err_msg)
                    api_communicator.notify_client(err_msg)

            # Last Status update of the job
            api_communicator.update_job_status()
            # Cleanup of local files
            cleanup.run(runtime_info.get_all())
        except BaseException as error:
            # api_communicator.notify_client("Error caught: {}".format(error))
            debug.log("Error caught: {}".format(error))
            debug.log("Traceback : {}".format(traceback.format_exc()))


if __name__ == '__main__':
    main(sys.argv[1:])
