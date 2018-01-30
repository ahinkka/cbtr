import operator
import os
import pickle
import random

from scipy.spatial import distance

import bottle
from bottle import route, run, request


with open('model.pickle', 'rb') as f:
    bundle = pickle.load(f)
article_id_to_id, id_to_article_id, term_doc_matrix = bundle


def cosine_distances(term_doc_matrix, index):
    distances = []
    for i in range(term_doc_matrix.shape[0]):
        if i == index:
            continue
        distances.append((i, distance.cosine(term_doc_matrix[index],
                                             term_doc_matrix[i])))
    return distances


@route('/')
@route('/<id>')
def root(id=None):
    count = request.query.count
    if count != '':
        count = int(count)
    else:
        count = 10

    if id is None:
        id = id_to_article_id[0]

    matrix_id = article_id_to_id[id]
    cos_neighbors = sorted(cosine_distances(term_doc_matrix, matrix_id),
                           key=operator.itemgetter(1), reverse=True)[0:count]

    for id, distance in cos_neighbors:
        print('{} => {}: {}'.format(id_to_article_id[matrix_id], id_to_article_id[id], distance))

    items = [id_to_article_id[id] for id, _ in cos_neighbors]
    return ','.join(items) + '\n'


bottle.debug(True)
run(host='0.0.0.0', port=8091)
