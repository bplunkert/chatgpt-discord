FROM python:latest

WORKDIR /app
COPY ./requirements.txt /app
RUN pip install --upgrade pip
RUN pip install -r requirements.txt
COPY * /app

ENTRYPOINT ["python", "app.py"]
