import random
import os

import bottle
from bottle import route, run, request


article_ids = []
with open('article_ids.txt', 'r') as f:
    for line in f:
        article_ids.append(line.strip())


@route('/')
@route('/<id>')
def root(id=None):
    count = request.query.count
    if count != '':
        count = int(count)
    else:
        count = 10

    items = random.choices(article_ids, k=count)
    return ','.join(items) + '\n'


bottle.debug(True)
run(host='0.0.0.0', port=8090)
