FROM python:2.7-alpine

RUN apk update && apk upgrade
RUN apk add poppler-utils libxslt-dev build-base
RUN apk --no-cache --update-cache add gcc gfortran python python-dev py-pip build-base wget freetype-dev libpng-dev openblas-dev

ADD requirements.txt /app/requirements.txt
RUN pip install -r /app/requirements.txt
RUN pip install --upgrade setuptools

ADD . /app
WORKDIR /app

ENV PYTHONPATH $PYTHONPATH:/app/

CMD ["python", "/app/bot.py"]
