FROM python:3.8.2

COPY . /src/math/

RUN pip install pipenv==2018.11.26

RUN cd /src/math/ && pipenv install --system --deploy

ENTRYPOINT ["python"]

CMD ["/src/math/math-api.py"] 