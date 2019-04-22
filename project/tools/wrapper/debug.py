import time


def log(string):
    timestamp = time.asctime()
    log = '[' + timestamp + '] - ' + str(string) + '\n'
    file = open("/tmp/debug.log", "a+")
    file.write(log)
    file.close()
