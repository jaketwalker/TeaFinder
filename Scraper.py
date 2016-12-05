"""
    Scraper.py
    Purpose: primary entry point to run product web scrapers and insert into the scraper database.
    To add a new scraper, import and add the imported function into SCRAPER_LIST.
    
    Created By: Jake Walker
    Created Date: 12/8/2016
"""

import ScraperDatabase as Database

"""ADD NEW SCRAPERS HERE:"""
from ScraperTemplates.TeasourceScraper import main as Teasource
from ScraperTemplates.CamelliaSinensisScraper import main as CamelliaSinensis
SCRAPER_LIST = [
    Teasource,
    CamelliaSinensis
    ]
    

def main():
    """
        Load items from scrapers into the database.
        For each product scraped, instantiate a ProductDB class to insert into the database.
    """
    # Scrape each website
    products = []
    for scraper in SCRAPER_LIST:
        products.extend(scraper())
    
    # Instantiate a ProductDB class for each product to insert into the database.
    productdb = []
    for product in products:
        productdb.append(
            Database.ProductDB(
                tea_name=product.name, 
                tea_type=product.type,
                tea_description=product.description,
                source_name=product.source,
                product_id=product.id,
                cost=product.cost, 
                url=product.url,
                image_url=product.image
                )
            )
    
    # Deactivate any products no longer available on websites
    Database.deactivate_products()
    
    return productdb


if __name__ == '__main__':
    main()