from abc import ABC, abstractmethod


class Executable(ABC):

    @staticmethod
    @abstractmethod
    def execute() -> None: ...


class SoloExecutable(Executable):
    """Module executed only once at startup"""


class IntervalExecutable(Executable):
    """Module executed at a regular interval (e.g. every 30s)"""

    interval: int
    """Number of seconds between executions"""
