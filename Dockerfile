FROM python:3.8.1-slim-buster

RUN apt-get update && \
    apt-get upgrade -y

ENV FLASK_ENV development

WORKDIR .

COPY . .

RUN pip install -r requirements.txt

EXPOSE 5000

ENTRYPOINT ["gunicorn", "-w 2","-b 0.0.0.0:5000", "wsgi:app"]



