FROM python:3.9

ENV PYTHONPATH /app
WORKDIR /app

RUN apt-get -y update
#RUN apt-get install -y sqlite3 libsqlite3-dev build-essential

#RUN python3 -m pip install -U pip
#RUN python3 -m pip install -U setuptools

COPY ./requirements.txt requirements.txt
RUN pip3 install -r requirements.txt

COPY ./app/ /app/
ENTRYPOINT ["python3", "launcher.py"]