FROM python:3.8.2

COPY ./math .

RUN pip install pipenv

RUN pipenv install --system --deploy --ignore-pipfile

ENTRYPOINT ["python"]

CMD ["math.py"]