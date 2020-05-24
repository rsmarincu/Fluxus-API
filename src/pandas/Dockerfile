FROM python:3.8.2

COPY . /src/pandas/

RUN pip install pipenv

RUN cd /src/pandas/ && pipenv install --system --deploy

EXPOSE 5001

ENTRYPOINT ["python"]

CMD ["/src/pandas/pandas-api.py"] 