"""
For dealing with source data for decided which twitter accounts to scrape
"""

from __future__ import unicode_literals, print_function


def load_source(filename):
    with open(filename) as io:
        return list(line.strip() for line in io)
