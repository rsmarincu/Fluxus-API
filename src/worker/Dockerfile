FROM python:3.7 as base

RUN pip install pipenv==2018.11.26

COPY ./Pipfile /Pipfile
COPY ./Pipfile.lock /Pipfile.lock

RUN pipenv install --system --deploy

FROM base
COPY ./worker.py /worker.py
COPY ./rediswq.py /rediswq.py

CMD  python -W ignore worker.py