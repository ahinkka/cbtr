'''
terms are words in the corpus
set of all terms is the vocabulary
corpus consists of documents or articles
lda is a topic model that maps topics to terms
we are interested in document vectors (or embeddings)
in lda case document vectors are vectors of weights for each topic
this is left here as a joke so that every successive line is longer than the previous
'''
import collections
import operator
import os
import pickle

try:
    from sklearn.feature_extraction.text import CountVectorizer
    from sklearn.decomposition import LatentDirichletAllocation
except:
    pass
from scipy.spatial import distance

from patharg import PathType


Model = collections.namedtuple(
    'Model',
    'article_id_to_id, id_to_article_id, article_vector, topic_vector, feature_names')


def read_model(file):
    return pickle.load(file)


def read_articles(indir):
    result = {}

    for index, item in enumerate(os.listdir(indir)):
        id = item.strip().replace('.txt', '')
        with open(os.path.join(indir, item), 'r') as f:
            result[index] = (id, f.read())

    return result


def make_term_frequency_model(articles, n_features=1000):
    # n_features is basically the number of words from the vocab to include
    tf_vectorizer = CountVectorizer(max_df=0.95, min_df=2, max_features=n_features)
    result = tf_vectorizer.fit_transform(articles)
    print("Created a term-frequency model with shape", result.shape)
    return result, tf_vectorizer.get_feature_names()


def make_model(term_frequency_model, n_components=10):
    lda = LatentDirichletAllocation(n_components=n_components, max_iter=5,
                                    learning_method='online',
                                    learning_offset=50.,
                                    random_state=0)
    lda = lda.fit(term_frequency_model)
    # lda.components is a feature-topic matrix
    #  (i.e. rows are topics, cols are features, i.e. words)
    doc_topic_model = lda.transform(term_frequency_model)
    print("Created an LDA model\n", lda)
    print("Created a doc-topic-model of shape", doc_topic_model.shape)
    return lda, doc_topic_model


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
    term_doc_matrix, feature_names = make_term_frequency_model(contents_sorted_by_id)

    n_topics = 10
    best_model = None, None
    lowest_perplexity = 100000000
    while True:
        lda, doc_topic_model = make_model(term_doc_matrix, n_components=n_topics)
        perplexity = lda.perplexity(term_doc_matrix)
        print('Topic count', n_topics, 'PPL', perplexity)
        if perplexity < lowest_perplexity:
            best_model = lda, doc_topic_model
            lowest_perplexity = perplexity
            print('Best model, topic count', n_topics, 'with a perplexity of', perplexity)

        n_topics += 1
        if n_topics > 20:
            break

    result = Model(article_id_to_id=article_id_to_id, id_to_article_id=id_to_article_id,
                   article_vector=doc_topic_model, topic_vector=lda.components_,
                   feature_names=feature_names)
    return result


def write_model(file, model):
    pickle.dump(model, file)
    print('Model written to', file)


def print_top_words(topic, topic_idx, feature_names, n_top_words):
    # for topic_idx, topic in enumerate(model.components_):
    message = "Topic #%d: " % topic_idx
    message += " ".join([feature_names[i]
       for i in topic.argsort()[:-n_top_words - 1:-1]])
    print(message)


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
        if args.function == 'topics':
            for idx, topic in enumerate(model.topic_vector):
                print_top_words(topic, idx, model.feature_names, 10)
        elif args.function == 'articles':
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
