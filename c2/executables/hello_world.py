from .base import ExecutionModule, ExecutionTiming


class HelloWorldModule(ExecutionModule):

    @property
    def timing(self) -> ExecutionTiming:
        return ExecutionTiming.ONCE

    @staticmethod
    def execute() -> None:
        print("Hello, World!")
