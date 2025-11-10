import requests

from .common import IntervalExecutable


class HeartbeatModule(IntervalExecutable):
    """Send a heartbeat back to C2"""

    C2_DOMAIN = "http://localhost:8000"

    @staticmethod
    def execute() -> None:
        response = requests.post(url=HeartbeatModule.C2_DOMAIN + "/heartbeat")

        if response.status_code == 200:
            print(response.json())
        else:
            print(response.content)
    
    interval = 10