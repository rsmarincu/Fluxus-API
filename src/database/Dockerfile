FROM python:3.8.2

COPY . /src/database/

RUN pip install pipenv

RUN cd /src/database/ && pipenv install --system --deploy

EXPOSE 8080 7474 7687

ENTRYPOINT ["python"]

CMD ["-u", "/src/database/run.py"] 