#!/usr/bin/env python3

import os
import subprocess
import sys

path = sys.argv[-1]
current_path = os.path.dirname(os.path.abspath(__file__))

if path.startswith(current_path + "/project/"):
    path = path.replace(current_path + "/project/", "/src/")
    subprocess.run(
        [
            "docker-compose",
            "exec",
            "-T",
            "web",
            "sh",
            "-c",
            "PYTHONPATH=/src/extrasrc autopep8 {} {}".format(
                " ".join(sys.argv[1:-1]), path
            ),
        ],
        stdout=sys.stdout,
    )
else:
    subprocess.run([os.environ["HOME"] + "/.local/bin/autopep8"] + sys.argv[1:])
