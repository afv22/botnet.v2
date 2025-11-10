from dotenv import load_dotenv

load_dotenv()

from flask import Flask, request
from flask_cors import CORS

from db import Bot, init_db

app = Flask(__name__)
app.config["SECRET_KEY"] = "dev-secret-key"

CORS(app)

init_db(app)


@app.route("/heartbeat")
def heartbeat():
    if not request.remote_addr:
        raise RuntimeError("No IP found")

    print(f"Heartbeat from {request.remote_addr}")
    Bot.heartbeat(request.remote_addr)

    return {"status": "ok"}


if __name__ == "__main__":
    app.run(debug=True, port=8000)
