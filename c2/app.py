from typing import List
from dotenv import load_dotenv

load_dotenv()

from flask import Flask, request, send_from_directory
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


@app.get("/updates")
def get_updates():
    latest_version = request.args.get("version")
    if not latest_version:
        raise RuntimeError("No Version number")

    return {"filenames": Version.list_modified_files(int(latest_version))}


@app.get("/updates/<filename>")
def get_updated_file(filename):
    return send_from_directory("executables", filename)


@app.post("/updates/register")
def register_updates():
    data = request.json
    if not data:
        raise RuntimeError("Shit")

    filenames: List[str] = data.get("filenames", "").split(",")
    return {"new_version": Version.register_new_vesion(filenames)}


if __name__ == "__main__":
    app.run(debug=True, port=8000)
