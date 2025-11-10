from abc import ABC, abstractmethod
from enum import Enum
from typing import Dict, Type, cast

import inspect
from importlib import import_module
from pathlib import Path


class Cadence(Enum):
    ONCE = "ONCE"


class Executable(ABC):

    @property
    @abstractmethod
    def timing(self) -> Cadence: ...

    @staticmethod
    @abstractmethod
    def execute() -> None: ...


class ExecutableManager:
    def __init__(self) -> None:
        exec_dir = Path(__file__).parent

        # Get all Python files except __init__.py and the base module
        module_files = [
            f for f in exec_dir.glob("*.py") if f.stem not in ("__init__", "common")
        ]

        self.modules: Dict[str, Type[Executable]] = {}

        for module_file in module_files:
            # Import the file as a module
            module_name = "executables." + module_file.stem
            module = cast(Executable, import_module(module_name))

            # Execute the executable within the module
            for _, obj in inspect.getmembers(module, inspect.isclass):
                if issubclass(obj, Executable) and obj is not Executable:
                    self.modules[module_name] = obj
                    break

    def execute_all(self) -> None:
        for _, mod in self.modules.items():
            mod.execute()
