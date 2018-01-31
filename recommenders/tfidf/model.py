import collections
import operator
import os
import pickle

try:
    from sklearn.feature_extraction.text import TfidfVectorizer
except:
    pass
from scipy.spatial import distance

from patharg import PathType


Model = collections.namedtuple(
    'Model',
    'article_id_to_id, id_to_article_id, article_vector, feature_names')


def read_model(file):
    return pickle.load(file)


def read_articles(indir):
    result = {}

    for index, item in enumerate(os.listdir(indir)):
        id = item.strip().replace('.txt', '')
        with open(os.path.join(indir, item), 'r') as f:
            result[index] = (id, f.read())

    return result


# TODO: we should precompute all similarities as per
#       https://stackoverflow.com/a/12128777, now we use the feature vectors
def make_tfidf_model(articles, n_features=1000):
    # n_features is basically the number of words from the vocab to include
    tfidf_vectorizer = TfidfVectorizer(max_df=0.95, min_df=2, max_features=n_features)
    # result is a term-document matrix
    result = tfidf_vectorizer.fit_transform(articles)
    print("Created a term-frequency-inverse-document-frequency model with shape", result.shape)
    return result.toarray(), tfidf_vectorizer.get_feature_names()


def build_model(indir):
    articles = read_articles(indir)
    print('Read {} articles'.format(len(articles)))

    id_to_content = {}
    id_to_article_id = {}
    article_id_to_id = {}
    for id, triple in articles.items():
        id_to_article_id[id], id_to_content[id] = triple
        article_id_to_id[triple[0]] = id

    contents_sorted_by_id = [b
                             for a, b in sorted(id_to_content.items(),
                                                key=operator.itemgetter(0))]
    term_doc_matrix, feature_names = make_tfidf_model(contents_sorted_by_id)

    result = Model(article_id_to_id=article_id_to_id, id_to_article_id=id_to_article_id,
                   article_vector=term_doc_matrix, feature_names=feature_names)
    return result


def write_model(file, model):
    pickle.dump(model, file)
    print('Model written to', file)


def cosine_distances(term_doc_matrix, index):
    distances = []
    for i in range(term_doc_matrix.shape[0]):
        if i == index:
            continue
        distances.append((i, distance.cosine(term_doc_matrix[index],
                                             term_doc_matrix[i])))
    return distances


def recommend(model, matrix_id, count):
    cos_neighbors = sorted(cosine_distances(model.article_vector, matrix_id),
                           key=operator.itemgetter(1), reverse=True)[0:count]

    return cos_neighbors


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(help='sub-command help', dest='command')

    build_parser = subparsers.add_parser('build', help='build help')
    build_parser.add_argument('corpusdir', type=PathType(exists=True, type='dir'))
    build_parser.add_argument('modelfile', type=argparse.FileType('wb'))

    query_parser = subparsers.add_parser('query', help='query help')
    query_parser.add_argument('model', type=argparse.FileType('rb'))
    query_parser.add_argument('function', choices=['articles', 'topics', 'recommend'])
    query_parser.add_argument('--document-id', required=False)
    args = parser.parse_args()

    if args.command == 'build':
        model = build_model(args.corpusdir)
        write_model(args.modelfile, model)
    elif args.command == 'query':
        model = read_model(args.model)
        if args.function == 'articles':
            for article_id in model.article_id_to_id.keys():
                print(article_id)
        elif args.function == 'recommend':
            if not args.document_id:
                parser.error("--document-id required for recommendations")
            matrix_id = model.article_id_to_id[args.document_id]
            recommendations = recommend(model, matrix_id, 20)
            for id, distance in recommendations:
                print('{}\t{}\t{}'.format(model.id_to_article_id[matrix_id],
                                          model.id_to_article_id[id], distance))
    else:
        parser.error('unknown command')
