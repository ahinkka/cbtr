import http.client
import random
import os
import socket
import urllib

from os import environ as env

import bottle
from bottle import route, run, request, redirect


articles = {}
for item in os.listdir(env['ARTICLE_DIR']):
    path = os.path.join(env['ARTICLE_DIR'], item)
    id = item.split('.txt')[0]

    with open(path, 'r') as f:
        name = f.readline().strip()

    articles[id] = {'path': path,
                    'id': id,
                    'name': name}


recommenders = {}
for rec in env['RECOMMENDERS'].split('|'):
    if rec.strip() == '':
        continue # allow no recommenders as an empty env var
    name, url = rec.split('::')
    recommenders[name] = url


@route('/')
def root():
    id = random.choice(list(articles.keys()))
    redirect('/article/' + id + '/')


# https://getbootstrap.com/docs/4.0/components/navs/#vertical


ARTICLE_TEMPLATE = '''
<!doctype html>
<html>
  <head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1, shrink-to-fit=no">
 
    <title>{title}</title>
    <link rel="stylesheet" href="https://maxcdn.bootstrapcdn.com/bootstrap/4.0.0/css/bootstrap.min.css" integrity="sha384-Gn5384xqQ1aoWXA+058RXPxPg6fy4IWvTNh0E263XmFcJlSAwiGgFAW/dAiS6JXm" crossorigin="anonymous">
  </head>
  <body>
    <br/>
    <br/>
    <div class="row">
      <div class="col-2"></div>
      <div class="col-5">
        <h1>{title}</h1>
        {contents}
      </div>
      <div class="col-1">{recommendations}</div>
    </div>

  </body>
</html>
'''


def fetch_recommendations(url, id, count):
    try:
        conn = http.client.HTTPConnection(url)
        conn.request("GET", "/" + id + "?count=" + str(count))
        r = conn.getresponse()
        if r.status != 200:
            raise Exception("got status " + repr(r.status))
        contents = r.read().decode("utf-8")

        result = []
        for item in contents.strip().split(','):
            result.append(item.strip())
        return result
    except socket.gaierror as sgai:
        raise Exception("URL, id, count: {}, {}, {}".format(url, id, count))


def render_recommendations_column_as_html(items, current_page_id): # name, id format
    tmp = []
    choices = ','.join([item[0] for item in items])
    for id, name, recommender in items:
        tmp.append('<li class="nav-item"><a class="nav-link" href="/article/{}/?ref={}&rec={}&choices={}">{}</a></li>'.format(id, current_page_id, recommender, choices, name))

    return '<ul class="nav flex-column">\n' + '\n'.join(tmp) + '\n</ul>'


@route('/article/<id>/')
def article(id):
    ref = request.query.ref
    rec = request.query.rec
    choices = request.query.choices

    if ref != '' and rec != '' and choices != '':
        print(ref, rec, choices.split(','))
        # TODO: implement reporting to an "analytics backend"

    article_pool = []
    for recommender_name, recommender_url in recommenders.items():
        # in reality this would not be done like this (aggregating service via AJAX more likely)
        recs = fetch_recommendations(recommender_url, id, 20)
        for rec in recs:
            name = articles[rec]['name']
            article_pool.append((rec, name, recommender_name))

    if len(article_pool) > 0:
        used_recs = random.choices(article_pool, k=10)

        # Remove duplicates
        eff_recs = []
        eff_rec_in = set()
        for rec in used_recs:
            if rec[0] not in eff_rec_in:
                eff_recs.append(rec)
                eff_rec_in.add(rec[0])

        # TODO: remove duplicates from multiple recommendation backends
        recommendations = render_recommendations_column_as_html(eff_recs, id)
    else:
        recommendations = ''

    with open(articles[id]['path'], 'r') as f:
        title = articles[id]['name']
        return ARTICLE_TEMPLATE.format(title=title, contents=''.join(f.readlines()[1:]),
                                       recommendations=recommendations)


bottle.debug(True)
run(host='0.0.0.0', port=8080)
