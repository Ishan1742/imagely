FROM python:3.8

LABEL MAINTAINER="Ishan Ghosh <ghosh.ishang@gmail.com>"

RUN pip3 install pipenv

WORKDIR /usr/src/app

COPY Pipfile ./
COPY Pipfile.lock ./

RUN set -ex && pipenv install --deploy --system

COPY . .

EXPOSE 5000

CMD ["python", "app.py"]
