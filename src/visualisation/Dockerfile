FROM python:3.8.2

COPY . /src/visualisation/

RUN pip install pipenv

RUN cd /src/visualisation/ && pipenv install --system --deploy

EXPOSE 5002

ENTRYPOINT ["python"]

CMD ["/src/visualisation/visualisation-api.py"] 