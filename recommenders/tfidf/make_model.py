import pickle
import os

from sklearn.feature_extraction.text import TfidfVectorizer

from patharg import PathType


def read_articles(indir):
    result = {}

    for index, item in enumerate(os.listdir(indir)):
        id = item.strip().replace('.txt', '')
        with open(os.path.join(indir, item), 'r') as f:
            lines = f.readlines()
            title = lines[0].strip()
            contents = '\n'.join(lines[1:])
            result[index] = (id, title, contents)

    return result


def make_tfidf_model(articles, n_features=1000):
    # n_features is basically the number of words from the vocab to include
    tfidf_vectorizer = TfidfVectorizer(max_df=0.95, min_df=2, max_features=n_features)
    # result is a term-document matrix
    return tfidf_vectorizer.fit_transform(articles)


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('indir', type=PathType(exists=True, type='dir'))
    parser.add_argument('outfile', type=argparse.FileType('wb'))
    args = parser.parse_args()

    articles = read_articles(args.indir)
    print('Read {} articles'.format(len(articles)))

    id_to_content = {}
    id_to_title = {}
    id_to_article_id = {}
    article_id_to_id = {}
    for id, triple in articles.items():
        id_to_article_id[id], id_to_title[id], id_to_content[id] = triple
        article_id_to_id[triple[0]] = id

    contents_sorted_by_id = [b
                             for a, b in sorted(id_to_content.items(),
                                                key=operator.itemgetter(0))]
    term_doc_matrix = make_tfidf_model(contents_sorted_by_id).toarray()

    bundle = article_id_to_id, id_to_article_id, term_doc_matrix
    pickle.dump(bundle, args.outfile)
