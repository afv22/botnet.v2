import time
import requests

C2_DOMAIN = "http://localhost:8000"


def main():
    while True:
        response = requests.get(url=C2_DOMAIN + "/heartbeat")
        print(response.json())
        time.sleep(1)


if __name__ == "__main__":
    try:
        main()
    finally:
        print("Shutting down...")
