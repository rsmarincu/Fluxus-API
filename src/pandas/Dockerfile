FROM python:3.8.2

COPY . /src/pandas/

RUN pip install pipenv==2018.11.26

RUN cd /src/pandas/ && pipenv install --system --deploy

ENTRYPOINT ["python"]

CMD ["/src/pandas/pandas-api.py"] 