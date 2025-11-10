from .common import SoloExecutable


class HelloWorldModule(SoloExecutable):

    @staticmethod
    def execute() -> None:
        print("Hello, World!")
