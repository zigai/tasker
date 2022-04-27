import os
import sys

from tasker.task import Task


def cli():
    if len(sys.argv) != 2:
        print("Tasker usage:")
        print(f"\t{sys.argv[0]} run <path>")
        print(f"\t{sys.argv[0]} new <path>")
        exit(0)

    if sys.argv[1] == "run":
        task = Task.from_file(sys.argv[2])
        task.print()
        task.run()

    else:
        if sys.platform == "win32":
            exit(os.system(f"python {sys.argv[0]}"))
        else:
            exit(os.system(f"python3 {sys.argv[0]}"))


if __name__ == '__main__':
    cli()
