from enum import Enum
import os

basedir = os.path.abspath(os.path.dirname(__file__))


class ValidEnvironments(Enum):
    """Enum to control valid environment config inputs"""

    Development = ("Development",)
    Local = ("Local",)
    Test = ("Test",)
    Production = ("Production",)


class Default:
    """Default configuration that all enviroments will default to."""

    APP_NAME = "sfm"
    TESTING = True
    ENV = os.environ.get("ENV") or ValidEnvironments.Development
    SERVER = os.environ.get("SERVER") or "localhost"
    SECRET_KEY = "secret_key"
    WKHTMLTOPDF_BIN_PATH = "/usr/local/bin/"
    PDF_DIR_PATH = os.path.join(
        os.path.dirname(os.path.abspath(__file__)), "static", "pdf"
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False


class Development(Default):
    """Development environment"""

    DEBUG = True
    TESTING = False
    ENV = os.environ.get("ENV" or ValidEnvironments.Development)
    SQLALCHEMY_DATABASE_URI = os.environ.get("DATABASE_URL")
    SQLALCHEMY_TRACK_MODIFICATIONS = True


class Local(Default):
    """Local environment for development, testing, not in docker."""

    DEBUG = True
    TESTING = False
    ENV = os.environ.get("ENV") or ValidEnvironments.Development
    SQLALCHEMY_DATABASE_URI = os.environ.get("DATABASE_URL")


class Test(Default):
    """Continuous Integration (CI) / User Acceptance"""

    DEBUG = False
    TESTING = True
    ENV = os.environ.get("ENV") or ValidEnvironments.Test
    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"
    WTF_CSRF_ENABLED = False


class Production(Default):
    """Production"""

    DEBUG = False
    TESTING = False
    ENV = os.environ.get("ENV") or ValidEnvironments.Production
    SQLALCHEMY_DATABASE_URI = "postgresql://postgres:temp@postgres:5432/production"
