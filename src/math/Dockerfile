FROM python:3.8.2

RUN pip install pipenv==2018.11.26

COPY . /src/math/

RUN cd /src/math/ && pipenv install --system --deploy

ENTRYPOINT ["python"]

CMD ["/src/math/math-api.py"] 