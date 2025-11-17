FROM python:3.12-slim

ENV PORT=8080

WORKDIR /app

COPY ./requirements.in /app

RUN pip install --no-cache-dir pip-tools

RUN pip-compile --upgrade

RUN pip install --no-cache-dir -r requirements.txt

COPY . /app

CMD [ "python", "run.py" ]