from flask import Flask, request
from flask_cors import CORS

app = Flask(__name__)
app.config["SECRET_KEY"] = "dev-secret-key"

CORS(app)


@app.post("/heartbeat")
def heartbeat():
    print(f"Heartbeat from {request.remote_addr}")
    return {"status": "ok"}


if __name__ == "__main__":
    app.run()
