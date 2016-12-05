"""
    CommonScraper.py
    Purpose: Common helper functions for generating web scrapers for teas.db products.
    
    Created By: Jake Walker
    Created Date: 12/8/2016
"""

from bs4 import BeautifulSoup
import urllib.request

# Set scraper config
MAX_ATTEMPTS = 3                # max number of urlib requests for each site before skipping
MAX_AGE_BEFORE_DEACTIVATE = 14  # max time (days) since a product is last updated in the db before deactivating in our db.


class Product:
    """
        Class to store each product scraped off a source's wesbite.
        Any items added to this class may also need to be added to the ProductDB class using the teas.db sqlite database
            as of the first publish of this program.
    """
    def __init__(self, name, description, cost, source, id, url, type, image=""):
        self.name = name.strip()
        self.description = description.strip()
        self.cost = cost
        self.source = source
        self.url = url.strip()
        self.id = id.strip()
        self.type = type.strip()
        self.image = image

    def __str__(self):
        return "Source: {source}, Name: {name}".format(
            name=self.name,
            source=self.source
        )


def parse_page(url, parser, try_counter=0):
    """
        Convert a website by URL into a BeautifulSoup parser object.
        params: 
            'url': URL of website to parse
            'parser': parser interpretter.  ex. "HTML", "LXML", "XML".  See bs4 documentation.
            'try_counter': number of attempts already to access URL already.  Will skip URL after attempting a
                max number of times set by config variable MAX_ATTEMPTS.
    """
    html = None
    if try_counter <= MAX_ATTEMPTS:
        # Attempt to access URL.  If not, recursively call until try_counter > MAX_ATTEMPTS.
        try:
            html = urllib.request.urlopen(url)
        except urllib.error.HTTPError:
            parse_page(url, parser, try_counter + 1)

    if not html:
        return False
    return BeautifulSoup(html, parser)


def grams_to_oz(weight):
    """Convert grams into ounces.  Our db take ounces only."""
    return weight * 0.035274