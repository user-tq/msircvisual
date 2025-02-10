import time


def timestamp():
    return time.strftime("%m/%d/%y %H:%M:%S")


def tprint(string):
    output = string.split("\t")
    for line in output:
        print("[{0}] {1}".format(timestamp(), line))
