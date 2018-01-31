import argparse
import re
import os

from patharg import PathType
import nltk
from nltk.tokenize import word_tokenize
# from nltk.corpus import stopwords

PUNCTUATION = ('.', ',', ':', ';', "''", '""', '(', ')', '{', '}')


def strip_html(data):
    p = re.compile(r'<.*?>')
    return p.sub('', data)


def handle_file(infile, outfile, stopwords, stemmer):
    words = word_tokenize(strip_html(infile.read()))
    lowercase_words = [w.lower() for w in words]
    punctuation_removed = [w for w in lowercase_words if w not in PUNCTUATION]
    stopwords_removed = [w for w in punctuation_removed if w not in stopwords]
    stems = [stemmer.stem(w) for w in stopwords_removed]
    outfile.write(' '.join(stems))


def main(indir, outdir, language):
    nltk.download('stopwords')
    nltk.download('punkt')

    stopwords = set(nltk.corpus.stopwords.words(language))

    if language == 'finnish':
        stemmer = nltk.stem.SnowballStemmer('finnish')
        # stemmer = nltk.stem.snowball.FinnishStemmer()
    elif language == 'english':
        stemmer = nltk.stem.SnowballStemmer('english')
    else:
        raise Exception('unknown language {}'.format(language))

    for item in os.listdir(indir):
        infile = os.path.join(indir, item)
        outfile = os.path.join(outdir, item)

        with open(infile, 'r') as f1:
            with open(outfile, 'w') as f2:
                handle_file(f1, f2, stopwords, stemmer)


if __name__ == '__main__':
    import argparse
    from patharg import PathType
    parser = argparse.ArgumentParser()

    parser.add_argument('indir', type=PathType(exists=True, type='dir'))
    parser.add_argument('outdir', type=PathType(exists=True, type='dir'))

    # parser.add_argument('--stopwords-file', type=argparse.FileType('r'))
    parser.add_argument('--language', choices=['english', 'finnish'], required=True)

    args = parser.parse_args()
    main(args.indir, args.outdir, args.language)
