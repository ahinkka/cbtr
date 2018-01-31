# Content

Naturally content could be anything, but for easy and open testing purposes a
Wikipedia corpus is probably a good choice.

Wikipedia Monolingual Corpora from
http://linguatools.org/tools/corpora/wikipedia-monolingual-corpora/

Get a corpus:

`wget -O enwiki-20140707-corpus.xml.bz2 https://www.dropbox.com/s/j8kg3q6r7v7afd1/enwiki-20140707-corpus.xml.bz2?dl=0`

And extract it.

`bunzip2 enwiki-20140707-corpus.xml.bz2`

Get the tool to extract raw text:

`wget -O xml2txt.pl https://www.dropbox.com/s/p3ta9spzfviovk0/xml2txt.pl?dl=0`

Extract list of categories given a search string (to further extract only a subset of the corpus):

`python3 list_categories_inclusive.py <term> > included_categories.txt`

Extract the raw text for the corpus subset:

`perl xml2txt.pl fiwiki-20140809-corpus.xml output.txt -only-categories included_categories.txt -articles -p -h -nomath -nodisambig`

Further actually extract into separate files per article:

`mkdir ../ui/articles`

`python3 extract_to_files.py output.txt ../ui/articles`

Prepare a stemmed and stopword-removed version for the models:

`python3 stem_and_remove_stop_words.py ../ui/articles articles --language <language>`

Prepare models:

`python3 ../recommenders/random/make_model.py articles-cleaned ../recommenders/random/article_ids.txt`
`python3 ../recommenders/tfidf/make_model.py articles-cleaned ../recommenders/tfidf/model.pickle`

