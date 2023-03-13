import sys

from . import core

if __name__ == "__main__":
    args = sys.argv
    core.main(args[1], args[2], args[3])
