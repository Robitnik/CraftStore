import os
import subprocess
from modules.config import BASE_DIR


def migrate():
    py_commmand = "python"
    manage_py = os.path.join(BASE_DIR, "manage.py")
    commands = [f"{py_commmand} {manage_py} makemigrations", f"{py_commmand} {manage_py} migrate"]
    for c in commands:
        subprocess.run(c)


def global_migrate():
    pass

