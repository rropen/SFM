FROM tiangolo/uvicorn-gunicorn-fastapi:python3.9
RUN curl https://packages.microsoft.com/keys/microsoft.asc | apt-key add -
RUN curl https://packages.microsoft.com/config/ubuntu/21.04/prod.list > /etc/apt/sources.list.d/mssql-release.list
RUN apt-get update
RUN ACCEPT_EULA=Y apt-get install -y --allow-unauthenticated msodbcsql17
RUN ACCEPT_EULA=Y apt-get install -y --allow-unauthenticated mssql-tools 
RUN echo 'export PATH="$PATH:/opt/mssql-tools/bin"' >> ~/.bashrc source ~/.bashrc
RUN apt-get install -y unixodbc-dev


RUN apt-get update \
    && apt-get upgrade -y \
    && apt-get install -y \
    && apt-get -y install unixodbc unixodbc-dev apt-utils netcat gunicorn libpq-dev python3-dev gcc libpq-dev build-essential vim \
    && apt-get autoremove -y \
    && apt-get clean all
RUN pip install --upgrade pip setuptools wheel


COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
# COPY ./main.py __pypackages__/3.9/lib/sqlmodel

CMD ["uvicorn","sfm.main:app", "--workers", "4", "--host", "0.0.0.0", "--port","8181"]
# CMD ["uvicorn","sfm.main:app", "--workers", "4", "--host", "0.0.0.0", "--port","8181", "--reload"]

EXPOSE 8181