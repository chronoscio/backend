#!/usr/bin/env python
import os
import sys

# Remote Debugging
import ptvsd
import socket

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.close()
try:
    ptvsd.enable_attach("my_secret", address=("0.0.0.0", 3500))
except BaseException:
    pass


if __name__ == "__main__":
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "interactivemap.settings")
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc
    execute_from_command_line(sys.argv)
