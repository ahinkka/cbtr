# FROM python:3.6-alpine
# FROM alpine:3.7
FROM alpine:edge
MAINTAINER Atte Hinkka
EXPOSE 8091/tcp

RUN echo http://dl-cdn.alpinelinux.org/alpine/edge/testing >> /etc/apk/repositories
RUN apk update

RUN apk add --update python3
RUN apk add --update py3-numpy py3-scipy

COPY app.py /app.py
COPY patharg.py /patharg.py
COPY model.py /model.py
COPY bottle.py /bottle.py
COPY model.pickle /model.pickle

ENTRYPOINT ["python3.6"]
CMD ["/app.py"]
