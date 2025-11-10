import inspect
import time
from datetime import datetime, timedelta
from importlib import import_module
from pathlib import Path

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.executors.pool import ProcessPoolExecutor


from executables.common import SoloExecutable, IntervalExecutable


EXECUTABLES_DIR = "executables"


def main():
    executors = {"default": ProcessPoolExecutor(max_workers=5)}
    scheduler = BackgroundScheduler(executors=executors)

    # Get all Python files except __init__.py and the base module
    exec_dir = Path(__file__).parent / EXECUTABLES_DIR
    module_files = [
        f for f in exec_dir.glob("*.py") if f.stem not in ("__init__", "common")
    ]

    for module_file in module_files:
        # Import the file as a module
        module_name = f"{EXECUTABLES_DIR}.{module_file.stem}"
        module = import_module(module_name)

        # Execute the executable within the module
        for id, mod in inspect.getmembers(module, inspect.isclass):
            if issubclass(mod, SoloExecutable) and mod is not SoloExecutable:
                run_time = datetime.now() + timedelta(seconds=5)
                scheduler.add_job(mod.execute, "date", run_date=run_time)

            elif issubclass(mod, IntervalExecutable) and mod is not IntervalExecutable:
                scheduler.add_job(
                    mod.execute,
                    "interval",
                    seconds=mod.interval,
                    max_instances=1,
                    id=id,
                )

    scheduler.start()


if __name__ == "__main__":
    try:
        main()

        while True:
            time.sleep(1)
    finally:
        print("Shutting down...")
