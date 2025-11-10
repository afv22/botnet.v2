from dotenv import load_dotenv

load_dotenv()

from flask import Flask, request
from flask_cors import CORS

from db import init_db
from models import Bot, Version

app = Flask(__name__)
app.config["SECRET_KEY"] = "dev-secret-key"

CORS(app)

init_db(app)


@app.post("/heartbeat")
def heartbeat():
    if not request.remote_addr:
        raise RuntimeError("No IP found")

    Bot.heartbeat(request.remote_addr)

    return {
        "status": "ok",
        "version": Version.latest_version(),
    }


@app.get("/bots")
def get_bots():
    return [bot.json() for bot in Bot.all()]


if __name__ == "__main__":
    app.run(debug=True, port=8000)
