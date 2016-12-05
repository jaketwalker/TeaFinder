"""
    TeasourceScraper.py
    Purpose: scrape products from source TeaSource
    
    Notes:
        --Teasource has "collections" pages that classify their products.  Iterate over their collections and par
            out the URLs for each product.
        --Parses each of the product URLs
    
    Created By: Jake Walker
    Created Date: 12/8/2016
"""

import re

from ScraperTemplates.CommonScraper import Product, parse_page

# set config
MAIN_URL = "https://www.teasource.com/pages/tea-collection"
BASE_URL = "https://www.teasource.com"
COLLECTION_URL_SUFFIX = "?view=all"
TEA_TITLE_SPLITTER = " | "
PARSER = "lxml"
SOURCE = "TeaSource"
TEA_TYPE_MAP = {
    "Black Tea": "Black Tea",
    "Green Tea": "Green Tea",
    "White Tea": "White Tea",
    "Herbal Tea": "Herbal Tea",
    "Oolong Tea": "Oolong Tea"
    }


class Collection:
    def __init__(self, tea_type, link):
        self.tea_type = tea_type
        self.link = link

    def __str__(self):
        num_tabs = 3 if len(self.tea_type) < 10 else 2
        return "Tea type: {tea_type}{tabs}Link: {link}".format(tea_type=self.tea_type, tabs="\t"*num_tabs, link=self.link)


def get_tea_collection_urls(url):
    """Iterate over the site's collections and pull out the URLs of each product"""
    
    # Parse the current product list page.  If no page retrieved or if parser changes, return no webpage.
    soup = parse_page(url, PARSER)
    if not soup:
        return False

    # Get all items in the collection.  Kept as an unordered list on their page.
    collections = soup.find_all("li")
    lookup_collections = []
    for item in collections:
        
        # Parse out each product classification's name and URL
        link = item.find(name="div", class_="indiv-product")
        name = item.find(name="div", class_="hp-title")
        
        # If a valid collection, store in the collections list.  Normalize the tea type to our tea types.
        if link and name:
            link = link.a["href"]
            name = name.a.string
            if name in TEA_TYPE_MAP.keys():
                tea_type = TEA_TYPE_MAP[name]
                lookup_collections.append(Collection(tea_type, BASE_URL + link + COLLECTION_URL_SUFFIX))
    return lookup_collections


def get_product_urls(url):
    """Get a list of product URLs for each collection url passed"""
    
    # Parse the current product list page.  If no page retrieved or if parser changes, return no URLs.
    soup = parse_page(url, PARSER)
    if not soup:
        return False

    # Find each products "product grid" containing its details.  Find each product within each grid.
    product_grids = soup.find_all(class_=re.compile("product-grid"))
    for grid in product_grids:
        products_html = grid.find_all(class_="indiv-product")
        product_list = []
        for product in products_html:
            
            # Parse out the URL of any product in the product gris:
            href = product.a["href"]
            product_list.append(BASE_URL + href)
    return product_list


def get_products(product_links):
    """From a list of product URLs, pull details of the products."""
    products = []
    for collection, links in product_links.items():
        for link in links:
            
            # Parse the current product list page.  If no page retrieved or if parser changes, skip this URL.
            soup = parse_page(link, PARSER)
            if not soup:
                break

            # Parse out the title.  It contains both the title and tea type, so parse out just the title from the string.
            title = None
            if TEA_TITLE_SPLITTER in soup.find("title").string:
                title = soup.find("title").string.split(TEA_TITLE_SPLITTER)[0]

            # Parse the descriptions.  String together all pararaphs of the description.
            description_html = soup.find("div", class_="product-description-wrapper")
            description = description_html.string
            if not description:
                desc_paragraphs = [para.string.strip() for para in description_html.find_all("p") if para.string is not None]
                if desc_paragraphs and len(desc_paragraphs) > 0:
                    description = " ".join(desc_paragraphs)
            
            
            # Parse out the product image.  If the div tag contains an img tag, we can pull the img tag and the source URL.
            def image_tag(tag):
                """
                    Return True if a given HTML tag is an image tag.
                    bs4 documentation: https://www.crummy.com/software/BeautifulSoup/bs4/doc/#a-function
                """
                return tag.hasattr("img")
            image_html = soup.find("div", image_tag, class_="featured-image-div")
            image_url = image_html.find("img")
            if image_url:
                image_url = image_url["src"]

            
            # Parse out the item cost from the cost dropdown on the page.  Take the first cost option (assuming it is the
            # most expensive unit cost).  Assume the first in the cost dropdown is the smallest size you can purchase.
            cost = None
            product_variants = soup.find("div", id="product-variants")
            if not product_variants:
                continue
            first_product_variant = product_variants.find("option")
            if not first_product_variant.string or not first_product_variant["value"]:
                continue
            cost_string = first_product_variant.string
            id = first_product_variant["value"]
            
            # If a cost tag has found a potential product variant and cost, parse out the $ cost per the below regex.
            cost_reg_match = re.match(r'(\d+) ounces - \$ (\d+).(\d+)', cost_string)
            if cost_reg_match:
                dollar_cost = int(cost_reg_match.group(2)) + (float(cost_reg_match.group(3)) / 100)
                unit = int(cost_reg_match.group(1))
                cost = dollar_cost / unit


            # If all details are pulled, store the product.  Image is optional.
            if title and description and cost and id:
                products.append(Product(
                    name=title,
                    type=collection,
                    description=description,
                    cost=cost,
                    source=SOURCE,
                    id=id,
                    url=link,
                    image=image_url))
            
                # Print for status updates as scraper runs.
                print(products[-1])
            
    return products


def main():
    # Pull a distinct list of product URLs and parse it for product details.
    url_list = {}
    for coll in get_tea_collection_urls(MAIN_URL):
        url_list[coll.tea_type] = get_product_urls(coll.link)
    return get_products(url_list)


def _test():
    tea_collections = get_tea_collection_urls(MAIN_URL)
    print("Tea Collections:")
    for coll in tea_collections:
        print(coll)
    print("")

    url_list = {}
    for coll in [tea_collections[0]]:
        url_list[coll.tea_type] = get_product_urls(coll.link)[0:2]
    print("URLs:")
    for name, urls in url_list.items():
        num_tabs = 3 if len(name) < 10 else 2
        print("Name: {name}{tabs}URLs: {urls}".format(name=name, tabs="\t" * num_tabs, urls=urls))
    print("")

    # url_list = {"Green Tea": ["https://www.teasource.com/collections/green-tea/products/clouds-and-mist-supreme-green-tea"]}
    get_products(url_list)


if __name__ == '__main__':
    main()
    # _test()
