FROM python:3.8.2 

RUN pip install pipenv==2018.11.26

COPY . /src/database/

RUN cd /src/database/ && pipenv install --system --deploy

ENTRYPOINT ["python"]

CMD ["/src/database/run.py"] 