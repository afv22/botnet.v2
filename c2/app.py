from flask import Flask
from flask_cors import CORS

app = Flask(__name__)
app.config["SECRET_KEY"] = "dev-secret-key"

CORS(app)

if __name__ == "__main__":
    app.run()
