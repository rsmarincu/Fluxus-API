FROM python:3.7 as base-pandas
RUN pip install pipenv==2018.11.26
COPY ./Pipfile /Pipfile
COPY ./Pipfile.lock /Pipfile.lock

FROM base-pandas

COPY . /src/pandas/

RUN cd /src/pandas/

ENTRYPOINT ["python"]

CMD ["/src/pandas/pandas_api.py"] 