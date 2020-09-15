FROM python:3.7 as base-visualisation
RUN pip install pipenv==2018.11.26
COPY ./Pipfile /Pipfile
COPY ./Pipfile.lock /Pipfile.lock

FROM base-visualisation

COPY . /src/visualisation/

RUN cd /src/visualisation/

ENTRYPOINT ["python"]

CMD ["/src/visualisation/visualisation_api.py"] 