import time
import requests

C2_DOMAIN = "http://localhost:8000"


def main():
    while True:
        response = requests.post(url=C2_DOMAIN + "/heartbeat")
        
        if response.status_code == 200:
            print(response.json())
        else:
            print(response.content)
        
        time.sleep(10)


if __name__ == "__main__":
    try:
        main()
    finally:
        print("Shutting down...")
