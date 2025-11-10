from .common import Executable, Cadence


class HelloWorldModule(Executable):

    @property
    def timing(self) -> Cadence:
        return Cadence.ONCE

    @staticmethod
    def execute() -> None:
        print("Hello, World!")
