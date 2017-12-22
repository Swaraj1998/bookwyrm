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
from bs4 import BeautifulSoup as bs

DOMAINS = ('libgen.io', 'gen.lib.rus.ec')

def build_queries(item):
    """
    Build a set of Library Genesis search queries from an item.
    The set contains a pair: (query dictionary, path to index.php)
    """

    # Library Genesis divides its library into the following categories
    #   * LibGen (Sci-Tech) -- text books (/search.php);
    #   * Scientific Articles (/scimag/index.php);
    #   * Fiction (/foreignfiction/index.php);
    #   * Russion fiction (/fiction_rus/index.php; different structure; on hold);
    #   * Comics (/comics/index.php);
    #   * Standards (/standarts/index.php), and
    #   * Magazines (apparently only four, smartphone-related; ignored)
    #
    # To get everything we want, we aptly build a set set of queries that
    # searches all categories. We return a set of pairs holding the query dictionary,
    # and the path to the index.php, relative to domain root.
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
        'res': 100,  # 100 results per page
        'view': 'simple'
    }

    search_for_in = lambda req, col: queries.append(
        ({ **base, 'req': req, 'column': col}, '/search.php')
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
        'f_ext': item.exacts.extension or "All",
        'f_group': 0,  # Don't group results of differing extensions.
        'f_lang': 0,   # Search for all languages, for now.
    }

    fields = {'all': 0, 'title': 1, 'author': 2, 'series': 3}
    search_for_in = lambda s, col: queries.append(
        ({ **base, 's': s, 'f_column': col }, '/foreignfiction/index.php')
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

    queries.append(
        {
            's': ne.title,
            'journalid': ne.journal,
            'v': e.volume or e.year or '',  # e.volume should be a string
            #'i': add ne.issue?
            'p': e.pages,
            'redirect': 0
        },
        '/scimag/index.php'
    )

    #
    # The Comics Category
    #


    #
    # The Standards Category
    #

    #
    # The Magazines Category
    #

    return queries

if __name__ == "__main__":
    nonexacts = bw.nonexacts_t({
        'title': 'Victory of Eagles',
        'series': 'Temeraire',
        },

        ['Naomi Novik', 'Electric Banana Band']
    )

    item = bw.item((nonexacts, bw.exacts_t({},''), bw.misc_t([],[])))
    queries = build_queries(item)
    for query in queries:
        print(query)
