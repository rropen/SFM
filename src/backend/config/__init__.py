import os


SECRET_KEY = "secret_key"
ADMIN_KEY = "admin_key"
ALGORITHM = "HS256"

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
