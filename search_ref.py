#!/usr/bin/env python3
import argparse
import csv
import difflib
from pathlib import Path


CSV_FILE = Path(__file__).with_name('grocery_data_feb_2025_ref.csv')


def load_products(csv_path):
    with csv_path.open(newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        products = [row for row in reader]
    return products


def normalize_text(text):
    return (text or '').strip().lower()


def parse_search_query(query):
    words = normalize_text(query).split()
    if not words:
        return '', ''
    if len(words) == 1:
        return words[0], words[0]
    return words[0], normalize_text(query)


def find_best_match(query, products, title_field='title'):
    main_term, full_query = parse_search_query(query)
    if not main_term:
        return None, []

    def title_text(product):
        return normalize_text(product.get(title_field, ''))

    candidates = [product for product in products if main_term in title_text(product)]
    if not candidates:
        candidates = products

    full_query_title = full_query
    exact = [product for product in candidates if title_text(product) == full_query_title]
    if exact:
        return exact[0], exact

    substring = [product for product in candidates if full_query_title in title_text(product)]
    if substring:
        return substring[0], substring

    main_filter = [product for product in candidates if main_term in title_text(product)]
    if main_filter:
        titles = [title_text(product) for product in main_filter]
        matches = difflib.get_close_matches(full_query_title, titles, n=5, cutoff=0.4)
        if matches:
            best_title = matches[0]
            best = next((product for product in main_filter if title_text(product) == best_title), None)
            suggestions = [product for product in main_filter if title_text(product) in matches]
            return best, suggestions

    titles = [title_text(product) for product in candidates]
    matches = difflib.get_close_matches(full_query_title, titles, n=5, cutoff=0.4)
    if matches:
        best_title = matches[0]
        best = next((product for product in candidates if title_text(product) == best_title), None)
        suggestions = [product for product in candidates if title_text(product) in matches]
        return best, suggestions

    best = None
    best_score = 0.0
    for product in candidates:
        title = title_text(product)
        score = difflib.SequenceMatcher(None, full_query_title, title).ratio()
        if score > best_score:
            best_score = score
            best = product
    return best, [best] if best else []


def format_price(product):
    for field in ('pricing.displayPrice', 'pricing.price', 'pricing.memberOnlyPrice', 'pricing.mopDisplayPrice'):
        value = product.get(field, '')
        if value:
            return value
    return 'N/A'


def print_table(rows, headers):
    if not rows:
        return
    widths = [max(len(str(value)) for value in column) for column in zip(headers, *rows)]
    separator = '+' + '+'.join('-' * (width + 2) for width in widths) + '+'
    header_row = '| ' + ' | '.join(str(header).ljust(widths[i]) for i, header in enumerate(headers)) + ' |'

    print(separator)
    print(header_row)
    print(separator)
    for row in rows:
        print('| ' + ' | '.join(str(value).ljust(widths[i]) for i, value in enumerate(row)) + ' |')
    print(separator)


def display_search_results(best, suggestions):
    if not best:
        print('No matching product found.')
        return

    rows = []
    rows.append((1, best.get('title', 'Unknown'), best.get('productId', 'Unknown'), format_price(best)))
    other_matches = [product for product in suggestions if product is not best]
    for idx, product in enumerate(other_matches[:4], start=2):
        rows.append((idx, product.get('title', 'Unknown'), product.get('productId', 'Unknown'), format_price(product)))

    print('\nSearch results:')
    print_table(rows, ['#', 'Title', 'Product ID', 'Price'])
    if other_matches:
        print('\nDisplayed closest product first, then other close matches.')


def main():
    parser = argparse.ArgumentParser(description='Search grocery_data_feb_2025_ref.csv by item title and return the closest match.')
    parser.add_argument('query', nargs='?', help='Search query in two words: main product then full phrase')
    args = parser.parse_args()

    if not CSV_FILE.exists():
        raise SystemExit(f'CSV file not found: {CSV_FILE}')

    products = load_products(CSV_FILE)
    query = args.query

    while True:
        if not query:
            query = input('Enter search query (main product + full phrase, blank to exit): ').strip()

        if not query:
            print('Goodbye.')
            break

        best, suggestions = find_best_match(query, products)
        display_search_results(best, suggestions)

        query = input('\nNext search? Enter main product + full phrase or blank to quit: ').strip()


if __name__ == '__main__':
    main()


