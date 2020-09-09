FROM python:3.8.2

COPY . /src/visualisation/

RUN pip install pipenv==2018.11.26

RUN cd /src/visualisation/ && pipenv install --system --deploy

ENTRYPOINT ["python"]

CMD ["/src/visualisation/visualisation-api.py"] 