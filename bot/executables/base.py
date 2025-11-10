from abc import ABC, abstractmethod


class ExecutionModule(ABC):

    @staticmethod
    @abstractmethod
    def execute() -> None: ...
