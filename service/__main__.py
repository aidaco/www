import sys

from . import core, livecontrol, requestdb, staticfiles  # noqa: F401

if __name__ == "__main__":
    args = sys.argv
    core.main(args[1], args[2], args[3])
