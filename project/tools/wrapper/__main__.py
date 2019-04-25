import getopt
import sys
import traceback

from . import debug, setup, cleanup, execution


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
            setup.run(input_file)
            execution.run()
            cleanup.run()
        except Exception as error:
            debug.log("Error caught: {}".format(error))
            debug.log("Traceback : {}".format(traceback.format_exc()))


if __name__ == '__main__':
    main(sys.argv[1:])
