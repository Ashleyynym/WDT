import os
from datetime import timedelta
from dotenv import load_dotenv

load_dotenv()  # loads .env from project root, if present

basedir = os.path.abspath(os.path.dirname(__file__))

class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY") or "change_this_to_a_random_secret"
    SQLALCHEMY_DATABASE_URI = (
        os.environ.get("DATABASE_URL")
        or "sqlite:///" + os.path.join(basedir, "wdt_supplychain.db")
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Babel (i18n) settings
    BABEL_DEFAULT_LOCALE = "en"
    BABEL_SUPPORTED_LOCALES = ["en", "zh"]

    # Session lifetime (example)
    PERMANENT_SESSION_LIFETIME = timedelta(days=7)
