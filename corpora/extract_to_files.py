import os
import re
import unicodedata


def slugify(value):
    """
    Converts to lowercase, removes non-word characters (alphanumerics and
    underscores) and converts spaces to hyphens. Also strips leading and
    trailing whitespace.
    """
    value = unicodedata.normalize('NFKD', value).encode('ascii', 'ignore').decode('ascii')
    value = re.sub('[^\w\s-]', '', value).strip().lower()
    return re.sub('[-\s]+', '-', value)


def write_article(outdir, article_name, contents):
    outfile = os.path.join(outdir, slugify(article_name) + '.txt')
    if os.path.exists(outfile):
        return
    with open(outfile, 'w') as f:
        print(contents, file=f)
    # print(outdir, article_name, contents)


def extract(input, outdir):
    line_buffer = []
    current_article_name = None
    for line in input:
        if line.startswith('<article name="'):
            if current_article_name is not None:
                raise Exception('already current article or lines in buffer')

            beginning_cut = line.split('<article name="')[1]
            current_article_name = '"'.join(beginning_cut.split('"')[:-1])
            line_buffer = []
        elif line.startswith('</article>'):
            if current_article_name is None or len(line_buffer) == 0:
                raise Exception('no current article or no lines in buffer')

            write_article(outdir,
                          current_article_name,
                          ''.join([current_article_name] + line_buffer[1:-1]))
            current_article_name = None

        line_buffer.append(line)


if __name__ == '__main__':
    import argparse
    from patharg import PathType
    parser = argparse.ArgumentParser()
    parser.add_argument('infile', type=argparse.FileType('r'))
    parser.add_argument('outdir', type=PathType(exists=True, type='dir'))

    args = parser.parse_args()
    extract(args.infile, args.outdir)

    # categories = print_categories_inclusive(args.infile, args.searchterm)
