FROM python:latest

WORKDIR /app
COPY ./requirements.txt /app
RUN pip install -r requirements.txt
COPY * /app

ENTRYPOINT ["python", "app.py"]
