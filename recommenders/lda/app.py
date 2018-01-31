import operator
import os
import pickle
import random

import bottle
from bottle import route, run, request

import model
from model import Model


with open('model.pickle', 'rb') as f:
    model_ = pickle.load(f)


@route('/')
@route('/<id>')
def root(id=None):
    count = request.query.count
    if count != '':
        count = int(count)
    else:
        count = 10

    if id is None:
        id = model_.id_to_article_id[0]

    matrix_id = model_.article_id_to_id[id]
    recommendations = model.recommend(model_, matrix_id, count)

    # for id, distance in recommendations:
    #     print('{} => {}: {}'.format(model_.id_to_article_id[matrix_id],
    #                                 model_.id_to_article_id[id], distance))

    items = [model_.id_to_article_id[id] for id, _ in recommendations]
    return ','.join(items) + '\n'


bottle.debug(True)
run(host='0.0.0.0', port=8092)
