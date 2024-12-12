import os
import sys


def get_django_root(start_path):
    current_path = start_path
    while True:
        parent_path = os.path.dirname(current_path)
        os.chdir(current_path)
        for item in os.listdir(current_path):
            if os.path.isfile(item):
                if item == "manage.py":
                    return current_path

        if parent_path == current_path:
            # No more parent directories, root reached
            break
        current_path = parent_path


start_path = os.path.dirname(os.path.abspath(__file__))
root = get_django_root(start_path)
if root is None:
    raise Exception("Django root not found")
sys.path.insert(0, root)
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "core.settings")
os.environ["DJANGO_ALLOW_ASYNC_UNSAFE"] = "true"
import django

django.setup()
print("Playground is ready!")
