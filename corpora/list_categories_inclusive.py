import collections


def print_categories_inclusive(input, search_term, min_support):
    already_printed = set()
    matched_categories = set()
    inclusive_categories = collections.defaultdict(int)
    for line in input:
        if not line.startswith('<categories name="'):
            continue

        beginning_cut = line.split('<categories name="')[1]
        categories_name_attr = '"'.join(beginning_cut.split('"')[:-1])

        if len(categories_name_attr.strip()) == 0:
            continue

        categories = [cat.strip('*').strip() for cat in categories_name_attr.split('|')]

        is_match = False
        for cat in categories:
            if search_term in cat:
                matched_categories.add(cat)
                is_match = True
                break

        if is_match:
            for cat in categories:
                if cat not in matched_categories:
                    inclusive_categories[cat] += 1
                    if cat not in already_printed and inclusive_categories[cat] > min_support:
                        print(cat)
                        already_printed.add(cat)
                else:
                    if cat not in already_printed:
                        print(cat)
                        already_printed.add(cat)


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(
        description='list matching categories and categories these categories share pages with')
    parser.add_argument('searchterm')
    parser.add_argument('infile', type=argparse.FileType('r'))
    parser.add_argument('--min-support',
                        help='inclusive category must be shared by this many articles',
                        type=int, default=10)

    args = parser.parse_args()

    categories = print_categories_inclusive(args.infile, args.searchterm, args.min_support)
