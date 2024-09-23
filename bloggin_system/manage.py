#!/usr/bin/env python
"""Django's command-line utility for administrative tasks."""
import os
import sys
import subprocess

def run_fastapi():
    # Run FastAPI using Uvicorn on a different port
    subprocess.Popen(["uvicorn", "fastapi_app:app", "--port", "8001", "--reload"])

if __name__ == "__main__":
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "bloggin_system.settings")

    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc

    # Run FastAPI in a separate process only if specified
    if len(sys.argv) > 1 and sys.argv[1] == "runfastapi":
        run_fastapi()
        sys.exit()

    execute_from_command_line(sys.argv)

