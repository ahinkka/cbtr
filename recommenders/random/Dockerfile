FROM python:3.6-alpine
MAINTAINER Atte Hinkka
EXPOSE 8080/tcp

COPY app.py /app.py
COPY bottle.py /bottle.py
COPY article_ids.txt /article_ids.txt
ENTRYPOINT ["python3.6"]
CMD ["/app.py"]
