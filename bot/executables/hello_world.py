from .base import ExecutionModule


class HelloWorldModule(ExecutionModule):

    @staticmethod
    def execute() -> None:
        print("Hello, World!")
