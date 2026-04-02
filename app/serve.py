import os
import sys

if __package__ in (None, ""):
    sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from dotenv import load_dotenv
from waitress import serve

from app import create_app


load_dotenv(override=True)

app = create_app(os.getenv("APP_ENV", "production"))


if __name__ == "__main__":
    serve(app, host=app.config["HOST"], port=app.config["PORT"])
