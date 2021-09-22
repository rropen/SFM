import os
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = "sqlite:///./issues.db"
UI_URL = "http://localhost:3000"
SECRET_KEY = "secret_key"
ADMIN_KEY = "admin_key"
ALGORITHM = "HS256"

if os.environ.get("DATABASE_URL"):
    DATABASE_URL = os.environ.get("DATABASE_URL")
else:
    print("Database URL environment variable not set, using default.")

if os.environ.get("UI_URL"):
    UI_URL = os.environ.get("UI_URL")
else:
    print("UI URL environment variable not set, using default.")

if os.environ.get("SECRET_KEY"):
    SECRET_KEY = os.environ.get("SECRET_KEY")
else:
    print("Secret key environment variable not set, using default.")

if os.environ.get("ADMIN_KEY"):
    SECRET_KEY = os.environ.get("ADMIN_KEY")
else:
    print("Admin key environment variable not set, using default.")

if os.environ.get("ALGORITHM"):
    SECRET_KEY = os.environ.get("ALGORITHM")
else:
    print("Algorithm environment variable not set, using default.")
