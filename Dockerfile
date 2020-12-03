FROM python:3.8-slim

RUN apt-get update && \
    apt-get upgrade -y

ENV FLASK_ENV development

WORKDIR kasa

COPY requirements.txt .

RUN pip install pip -U

RUN pip install -r requirements.txt

EXPOSE 5000

ENTRYPOINT ["gunicorn","-b 0.0.0.0:5000", "wsgi:app"]



