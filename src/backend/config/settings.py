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
    ENV = os.environ.get("ENV") or ValidEnvironments.Test
    SERVER = os.environ.get("SERVER") or "localhost"
    SECRET_KEY = os.environ.get("SECRET_KEY") or "unset"
    SQLALCHEMY_TRACK_MODIFICATIONS = False


class Test(Default):
    """Unit Testing, Integration Testing"""

    DEBUG = False
    TESTING = True
    ENV = os.environ.get("ENV") or ValidEnvironments.Test
    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"
    SECRET_KEY = os.environ.get("SECRET_KEY") or "unset"
    WTF_CSRF_ENABLED = False


class Local(Default):
    """Local environment for development, testing, not in docker."""

    DEBUG = True
    TESTING = False
    ENV = os.environ.get("ENV") or ValidEnvironments.Local
    SQLALCHEMY_DATABASE_URI = os.environ.get("DATABASE_URL") or "sqlite:///./issues.db"
    SECRET_KEY = os.environ.get("SECRET_KEY") or "unset"


class Development(Default):
    """Development"""

    DEBUG = True
    TESTING = False
    ENV = os.environ.get("ENV") or ValidEnvironments.Development

    SQLALCHEMY_DATABASE_URI = os.environ.get("DATABASE_URL") or "unset"
    assert SQLALCHEMY_DATABASE_URI != "unset"  # mandate a connection string

    SECRET_KEY = os.environ.get("SECRET_KEY") or "unset"
    assert SECRET_KEY != "unset"

    SQLALCHEMY_TRACK_MODIFICATIONS = True


class Production(Default):
    """Production"""

    DEBUG = False
    TESTING = False
    ENV = os.environ.get("ENV") or ValidEnvironments.Production
    SQLALCHEMY_DATABASE_URI = os.environ.get("DATABASE_URL") or "unset"
    assert SQLALCHEMY_DATABASE_URI != "unset"  # mandate a connection string

    SECRET_KEY = os.environ.get("SECRET_KEY") or "unset"
    assert SECRET_KEY != "unset"

    SQLALCHEMY_TRACK_MODIFICATIONS = True
