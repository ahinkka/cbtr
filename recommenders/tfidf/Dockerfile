# FROM python:3.6-alpine
# FROM alpine:3.7
FROM alpine:edge
MAINTAINER Atte Hinkka
EXPOSE 8091/tcp

# RUN apk add --update python3
# RUN apk add --update make cmake gcc g++ gfortran
# RUN apk add --update python py-pip python-dev
# RUN apk add --update openblas-dev

# RUN pip install --no-cache-dir numpy scipy scikit-learn # pandas matplotlib
# COPY requirements.txt /requirements.txt
# RUN pip install --no-cache-dir -r /requirements.txt

# RUN apk del make cmake gcc g++ gfortran 
# RUN apk del py-pip python-dev
# RUN apk del openblas-dev

RUN echo http://dl-cdn.alpinelinux.org/alpine/edge/testing >> /etc/apk/repositories
RUN apk update

RUN apk add --update python3
RUN apk add --update py3-numpy py3-scipy

COPY app.py /app.py
COPY bottle.py /bottle.py
COPY model.pickle /model.pickle

ENTRYPOINT ["python3.6"]
CMD ["/app.py"]
