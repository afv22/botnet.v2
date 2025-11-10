from abc import ABC, abstractmethod
from enum import Enum


class ExecutionTiming(Enum):
    ONCE = "ONCE"


class ExecutionModule(ABC):

    @property
    @abstractmethod
    def timing(self) -> ExecutionTiming: ...

    @staticmethod
    @abstractmethod
    def execute() -> None: ...
