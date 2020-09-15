FROM python:3.8.2 as base-compute
RUN pip install pipenv==2018.11.26
COPY ./Pipfile /Pipfile
COPY ./Pipfile.lock /Pipfile.lock
RUN pipenv install --system --deploy

FROM base-compute as compute
COPY . .
ENTRYPOINT ["python"]

CMD ["-u", "compute.py"] 