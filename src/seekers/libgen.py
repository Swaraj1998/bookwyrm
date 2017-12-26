#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# This file is part of bookwyrm

# Copyright (C) 2017 Tmplt <tmplt@dragons.rocks>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

"""
Scrapes Library Genesis <https://en.wikipedia.org/wiki/Library_Genesis> for item matches.
"""

import pybookwyrm as bw
from bs4 import BeautifulSoup
from furl import furl
from collections import deque
import requests
import re
import isbnlib

DOMAINS = ('libgen.io', 'gen.lib.rus.ec')

def rows_from_url(url):
    r = requests.get(url)
    soup = BeautifulSoup(r.text, 'html.parser')
    table = soup.find('table', {'class': 'c', 'rules':'rows'}, recursive=False)

    for row in table.find_all('tr')[1:]:
        yield row


def build_queries(item):
    """
    Build a set of Library Genesis search queries from an item.
    The set contains a pair: (path to index.php, query dictionary)
    """

    # Library Genesis divides its library into the following categories:
    #   * LibGen (Sci-Tech) -- text books (/search.php);
    #   * Scientific Articles (/scimag/index.php);
    #   * Fiction (/foreignfiction/index.php);
    #   * Russion fiction (/fiction_rus/index.php; different structure; on hold);
    #   * Comics (/comics/index.php);
    #   * Standards (/standarts/index.php; different structure; on hold), and
    #   * Magazines (different structure (domain, et al.; on hold)
    #
    # Categories marked on hold may be implemented upon request.
    #    To get everything we want, we aptly build a set set of queries that
    # searches all categories. We return a set of pairs holding the query dictionary,
    # and the path to the index.php, absolute to domain root.
    #    Unfortunately, Library Genesis only allows to search one field at a time,
    # so when the wanted item specifies title AND authors AND publisher etc.,
    # we must do a query per field. Luckily, bookwyrm does the heavy lifting for us,
    # and some fields are unecessary, e.g. extension and year; these are not fuzzily matched.
    # TODO: investigate possibility of dupes. Hashmap?

    queries = []
    e = item.exacts
    ne = item.nonexacts

    #
    # The Text Book Category
    #

    # All appended queries below inherit the following keys
    base = {
        'req': 100,  # 100 results per page
        'view': 'simple'
    }

    search_for_in = lambda req, col: queries.append(
        ('/search.php', { **base, 'req': req, 'column': col})
    )

    if ne.title:
        search_for_in(ne.title, 'title')

    if ne.authors:
        search_for_in(', '.join(ne.authors), 'author')

    if ne.series:
        search_for_in(ne.series, 'series')

    if ne.publisher:
        search_for_in(ne.publisher, 'publisher')

    #
    # The Fiction Category
    #

    base = {
        'f_ext': e.extension or "All",
        'f_group': 0,  # Don't group results of differing extensions.
        'f_lang': 0,   # Search for all languages, for now.
    }

    fields = {'all': 0, 'title': 1, 'author': 2, 'series': 3}
    search_for_in = lambda s, col: queries.append(
        ('/foreignfiction/index.php', { **base, 's': s, 'f_column': col })
    )

    if ne.title:
        search_for_in(ne.title, fields['title'])

    if ne.authors:
        search_for_in(', '.join(ne.authors), fields['author'])

    if ne.series:
        search_for_in(ne.series, fields['series'])

    #
    # The Scientific Articles Category
    #

    def non_empty(*xs):
        res = [x for x in xs if x != bw.empty]
        return res[0] if res else None

    queries.append(
        ('/scimag/index.php',
        {
            's': ne.title,
            'journalid': ne.journal,
            'v': non_empty(e.volume, e.year),  # TODO: e.volume should be a string?
            #'i': add ne.issue?
            'p': non_empty(e.pages),
            'redirect': 0  # Don't redirect to Sci-Hub on no results
        })
    )

    return queries


def tables_fetcher(f):
    """
    A generator that given a start URL fetches each page of results.
    Yields a soup of the result table.
    """

    # While /search.php has a horizontal scrollbar that displays the current viewed page,
    # it is made with JavaScript, so we cannot use that. The second best way is probably
    # do check whether the current page fetch yields the same soup. If that's the case,
    # we've gone through all pages.

    p = 1
    query_params = f.args.copy()
    last_request = None

    while True:
        f.set({'page':p}).add(query_params)

        r = requests.get(f.url)
        if r.status_code != requests.codes.ok:
            # Log failure to bookwyrm?
            # Or log after taking exception?
            r.raise_for_status()

        if r.text == last_request:
            # We've gone through all pages.
            return

        soup = BeautifulSoup(r.text, 'html.parser')

        yield soup.find('table', {'class': 'c', 'rules':'rows'}, recursive=False)

        p += 1
        last_request = r.text

def translate_size(string):
    """
    Translate a size on the string form '1337 kb' and similar to a number of bytes.
    """
    try:
        count, unit = string.split(' ')
        count = int(count)
    except (ValueError, TypeError):
        return

    si_prefix = {
        'k': 1e3,
        'M': 1e6,
        'G': 1e9
    }

    # While LibGen lists sizes in '[kM]b', it's actually in bytes
    return int(count * si_prefix.get(unit[0]))


def process_libgen(table):
    """
    Processes a table soup and returns the items found within.
    """
    items = []

    if table == None:
        print("table is None")
        return

    def make_item(row):
        columns = row.find_all('td')

        # In a row, the first column contains the item's ID number on LibGen.
        # The other columns contain a single piece of data, the raw text of which
        # we aptly extract. The third column, however, contains the item's series
        # (in green cursive), title (blue), edition (cursive, green, in brackets),
        # and a number of ISBN numbers (green, cursive).
        #
        # Also, within this STEI (series, title, edition, isbsns) field, the title,
        # series, edition and isbsns are all in the same <a>-tag: fortunately,
        # the title is always in normal text, while the latter are both in their own
        # <font>-tags.

        authors, stei, publisher, year, pages, language, \
            size, extension = columns[1:9]
        mirrors = columns[9:-1]  # Last column is a link to edit the entry.

        # If first <a>-tag has title attribute, the item does not have a series.
        has_series = False if stei.a.has_attr('title') else True

        # The title, edition, and isbn section always contain an id-attribute with
        # an integer.
        tei = stei.find_next('a', id=re.compile('\d+$'))

        def extract_title():
            try:
                # The title is the first sibling of the first font tag, if any
                dd = deque(tei.font.previous_siblings, maxlen=1)
                return dd.pop()
            except AttributeError:
                # No edtion of isbn numbers
                return tei.text

        def extract_edition():
            # Always surrounded by brackets, so look for those.
            for font in tei.find_all('font', recursive=False):
                if font.text.startswith('[') and font.text.endswith(']'):
                    return font.text[1:-1]

        nonexacts = bw.nonexacts_t({
            'series': stei.a.text if has_series else '',
            'title': extract_title(),
            'publisher': publisher.text,
            'edition': extract_edition() or '',
            'language': language.text
        }, authors.text.split(', '))

        def try_toint(i):
            try:
                return int(i)
            except ValueError:
                return bw.empty

        exacts = bw.exacts_t({
            'year': try_toint(year.text),
            'pages': try_toint(pages.text),
            'size': translate_size(size.text) or bw.empty
        }, extension.text)

        def extract_isbns():
            valid_isbn = lambda isbn: isbnlib.is_isbn10(isbn) or isbnlib.is_isbn13(isbn)

            # Always comma-seperated, so split those and check all elements
            for font in tei.find_all('font', recursive=False):
                if font.text.startswith('[') and font.text.endswith(']'):
                    continue
                return [isbn for isbn in font.text.split(', ') if valid_isbn(isbn)]

        misc = bw.misc_t([mirror.a['href'] for mirror in mirrors], extract_isbns() or [])
        return (nonexacts, exacts, misc)

    # The first row is the column headers, so we skip it.
    for row in table.find_all('tr')[1:]:
        items.append(make_item(row))

    return items

if __name__ == "__main__":
    nonexacts = bw.nonexacts_t({
        'title': 'Victory of Eagles',
        'series': 'Temeraire',
        },

        ['Naomi Novik']
    )

    item = bw.item((nonexacts, bw.exacts_t({},''), bw.misc_t([],[])))
    queries = build_queries(item)
    books = []
    domain = DOMAINS[0]

    for query in queries:
        for domain in DOMAINS:
            path, params = query
            f = furl('http://' + domain + path).set(query_params=params)
            print(f.url)

            if path != '/search.php':
                continue

            try:
                for table in tables_fetcher(f):
                    if path == '/search.php':
                        books += process_libgen(table)
                    else:
                        print("unknown path")
            except ConnectionError:
                print("error: connection error")
                continue
            except requests.exceptions.HTTPError as e:
                print("http error:", e)
                continue

            # That domain worked; do the next query.
            break

    print('I found', len(books), 'books')
    for book in books:
        print(book)
