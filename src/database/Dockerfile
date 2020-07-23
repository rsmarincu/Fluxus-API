FROM python:3.8.2

COPY . /src/database/

RUN pip install pipenv==2018.11.26

RUN cd /src/database/ && pipenv install --system --deploy

ENTRYPOINT ["python"]

CMD ["-u", "/src/database/run.py"] 