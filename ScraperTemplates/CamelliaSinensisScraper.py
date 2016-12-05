"""
    CamelliaSinensisScraper.py
    Purpose: scrape products from source CamelliaSinensis
    
    Notes:
        --Gets product URLs from main site
        --Parses each of the product URLs
    
    Created By: Jake Walker
    Created Date: 12/8/2016
"""

import re

from ScraperTemplates.CommonScraper import Product, parse_page, grams_to_oz

# set config
MAIN_URL = "http://camellia-sinensis.com/en/tea?limit=100&mode=list&p="
MAX_BASE_PAGES = 25
PARSER = "lxml"
SOURCE = 'Camellia Sinensis'
TEA_TYPE_MAP = {
    "BLACK TEA": "Black Tea",
    "GREEN TEA": "Green Tea",
    "SCENTED TEA BLACK": "Black Tea",
    "SCENTED TEA GREEN": "Green Tea",
    "SCENTED TEA WHITE": "White Tea",
    "WHITE TEA": "White Tea",
    "WULONG AGED TEA": "Oolong Tea",
    "WULONG TEA": "Oolong Tea",
    "HERBAL TEA": "Herbal Tea",
    "ROOIBOS": "Herbal Tea"
    }
HTML_VALUE_REPLACEMENT = {
    "&#8232": ""
}


def get_product_links():
    """
        Get links to all available products from Camellia Sinensis.
        Website maxes at 100 items per page.  After accessing the last page, website returns the last page again.
            Iterate over unknown number of pages until we get repeat data.
    """
    
    # Keep a count of the number of items found and the page number
    reviewed_items = 0
    page_num = 1
    product_links = []
    
    # Iterate until we receive a duplicate page as the prior page or until a large number of pages accessed (to 
    # prevent any loops caused by changes to the unexpected changes to the webpage structure).
    while page_num <= MAX_BASE_PAGES:
        
        # Parse the current product list page.  If no page retrieved or if parser changes, end loop.
        url = MAIN_URL + str(page_num)
        soup = parse_page(url, PARSER)
        if not soup:
            break

        # Parse product count for the current page and update the total products viewed.
        # Product total is included in a span tag with item count "Items ###".  Iterate over
        # all span tags to find the item count.
        total = reviewed_items
        total_items = soup.find_all("span")  
        for item in total_items:
            item_value = ""
            if item.string:
                item_value = item.string
            total = re.match("Items (\d+)", item_value)
            # if an item count is found, parse out the count and update the total.
            if total:
                total = int(total.group(1))
                break
        # If no new items on this page, stop looking for product URLs since we have reached the end.
        if total <= reviewed_items:
            break
        else:
            # Set page parameters for next loop
            reviewed_items = total
            page_num += 1

        # Get all product details stoed in a div tag.  Pull out any URLs assumed to be product URLs.
        def parse_product_url(tag):
            """
                Return True if a given HTML tag contains a product URL.
                bs4 documentation: https://www.crummy.com/software/BeautifulSoup/bs4/doc/#a-function
            """
            if tag is None:
                return False
            elif tag.has_attr("class") and tag.has_attr("href") and tag.has_attr("title"):
                return tag["href"]
            else:
                return False
        
        # For each product, parse the product URLs.
        for details in soup.find_all("div", class_="infos clearfix"):
            for link_tag in details.find_all("a"):
                if parse_product_url(link_tag):
                    product_links.append(parse_product_url(link_tag))

    return product_links


def get_products(product_links):
    """
        Given a list of product URLs, parse product pages to get product details.
        Accepts a list of URL strings.    
    """

    products = []
    for url in product_links:
        
        # Attempt to parse the product URL
        soup = parse_page(url, PARSER)
        if not soup:
            continue

        # Parse the source's unique product ID.
        id_string = soup.find("p", class_="product-code").string
        id = re.search("PRODUCT CODE : (\S+)", id_string)
        if id:
            id = id.group(1)

        # Product details are generally kept on the right column of the website.
        details = soup.find("div", id="right-column")

        # Parse the product name and description from the right column.  String together all pararaphs of the description.
        name = details.find("p", class_="name").string
        description = " ".join(
            [para.string for para in details.find("div", class_="description").find_all("p") if para.string])
            
        # Certain HTML characters have been known to appear on this website and cause cross-browser compatibility issues.
        # Replace these values as they cause display issues in different browsers.
        for html_val in HTML_VALUE_REPLACEMENT.keys():
            if html_val in description:
                description = description.replace(html_val, HTML_VALUE_REPLACEMENT[html_val])

        # Parse the tea classification.  We will only map those included in the config.
        tea_type = details.find("p", class_="family").string
        if tea_type in TEA_TYPE_MAP.keys():
            tea_type = TEA_TYPE_MAP[tea_type]
        else:
            tea_type = None

        # Parse out the item cost from the cost dropdown on the page.  Take the first cost option (assuming it is the
        # most expensive unit cost).  Calculate the unit cost in ounces.  This site quotes in grams, so convert to ounces
        # for compatibility with our db.
        # Ignore all teas sold in boxes, bags, or gift sets.  Only include bulk-sold loose-leaf tea.  Assume quoted in grams.
        def is_cost_tag(tag):
            """
                Return True if a given HTML tag is from the page's cost dropdown.
                bs4 documentation: https://www.crummy.com/software/BeautifulSoup/bs4/doc/#a-function
            """
            return tag.name == "option" and tag.has_attr("data-saleable") and tag.has_attr("value")
            
        cost = None
        cost_tag = details.find(is_cost_tag)
        if cost_tag:
            cost = re.search("(\d+)g[ ]?[\xa0]?\$(\d+).(\d+)", cost_tag.string)
            if cost:
                cost_dollars = int(cost.group(2)) + (float(cost.group(3)) / 100)
                cost_weight = grams_to_oz(float(cost.group(1)))
                cost = cost_dollars / cost_weight
        
        # Images are all kept in the left column.  Go back to the original page parsed and look for the image overlay.
        image_html = soup.find("div", id="left-column").find_all("a", class_="img-overlay")
        image_url = ""
        for tag in image_html:
            if tag.has_attr("href"):
                image_url = tag["href"]

        # If all details are pulled, store the product.  Image is optional.
        if name and tea_type and description and cost and id:
            products.append(
                Product(
                    name=name,
                    type=tea_type,
                    description=description,
                    cost=cost,
                    source=SOURCE,
                    id=id,
                    url=url,
                    image=image_url)
                )
            
            # Print for status updates as scraper runs.
            print(products[-1])
        
    return products


def main():
    return get_products(get_product_links())


if __name__ == '__main__':
    main()
