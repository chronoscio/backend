FROM python:3.6-alpine
ENV PYTHONUNBUFFERED 1

RUN sed -i -e 's/v3\.7/edge/g' /etc/apk/repositories && \
    apk upgrade --update-cache --available

RUN apk update && \
    apk add --virtual build-deps gcc python-dev musl-dev && \
    apk add postgresql-dev bash && \
    apk add libressl2.7-libcrypto && \
    apk add --no-cache alpine-sdk && \
    apk add --no-cache --virtual .build-deps-testing \
        --repository http://dl-cdn.alpinelinux.org/alpine/edge/testing \
        gdal-dev \
        geos-dev \
        proj4-dev

RUN mkdir /config
ADD /config/requirements.txt /config/
RUN pip install -r /config/requirements.txt
RUN mkdir /src
WORKDIR /src
EXPOSE 80
CMD ["/bin/ash", "./init.sh", "gunicorn interactivemap.wsgi -b 0.0.0.0:80"]
