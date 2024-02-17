FROM python:latest
LABEL authors="ykhdr"

COPY . /src
WORKDIR /src
RUN pip install telebot sqlalchemy psycopg2

CMD ["python3", "/src/main.py"]