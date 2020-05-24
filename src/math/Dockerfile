FROM python:3.8.2

COPY . /src/math/

RUN pip install pipenv

RUN cd /src/math/ && pipenv install --system --deploy

ENTRYPOINT ["python"]

CMD ["/src/math/math-api.py"] 