def print_categories_inclusive(input, search_term):
    already_printed = set()
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
                is_match = True
                break

        if is_match:
            for cat in categories:
                if cat not in already_printed:
                    print(cat)
                    already_printed.add(cat)


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('searchterm')
    parser.add_argument('infile', type=argparse.FileType('r'))

    args = parser.parse_args()

    categories = print_categories_inclusive(args.infile, args.searchterm)
