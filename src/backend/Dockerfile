FROM tiangolo/uvicorn-gunicorn-fastapi:python3.9
RUN apt-get update \
    && apt-get upgrade -y \
    && apt-get install -y \
    && apt-get -y install unixodbc unixodbc-dev apt-utils netcat gunicorn libpq-dev python3-dev gcc libpq-dev build-essential vim \
    && apt-get autoremove -y \
    && apt-get clean all
RUN pip install --upgrade pip setuptools wheel

# WORKDIR /mec
COPY requirements.txt .
# COPY pyproject.toml .
# COPY pdm.lock .
# RUN pip install pdm
RUN pip install -r requirements.txt
# RUN pdm install --prod
COPY . .
# CMD ["pdm", "run", "uvicorn","mec.main:app", "--workers", "4", "--host", "0.0.0.0", "--port","8181", "--reload"]
CMD ["uvicorn","sfm.main:app", "--workers", "4", "--host", "0.0.0.0", "--port","8181", "--reload"]

EXPOSE 8181