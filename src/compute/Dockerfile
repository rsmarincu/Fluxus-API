FROM python:3.7 as base
COPY requirements.txt .
RUN pip install -r requirements.txt



FROM base as compute
COPY . .
ENTRYPOINT ["python"]

CMD ["-u", "compute.py"]