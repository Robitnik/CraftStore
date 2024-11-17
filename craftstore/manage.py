#!/usr/bin/env python
import os
import sys

def bd():
    os.system("poetry run python manage.py makemigrations")
    os.system("poetry run python manage.py migrate")
    os.system("clear")
    print("Міграції створенно")
    exit()

def main():
    if sys.argv[1] == "bd":
        bd()
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'craftstore.settings')
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc
    execute_from_command_line(sys.argv)


if __name__ == '__main__':
    main()
