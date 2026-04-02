import os
import sys

if __package__ in (None, ""):
    sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from app import create_app
from dotenv import load_dotenv

load_dotenv(override=True)

app = create_app(os.getenv("APP_ENV", "development"))

if __name__ == "__main__":
    app.run(
        host=app.config["HOST"],
        port=app.config["PORT"],
        debug=app.config["DEBUG"],
    )
