"""
    ScraperDatabase.py
    Purpose: 
        Defines database, functions, classes and methods for iinserting products into the teas.db database.
        Contains _test() function to test assumed functionality within the database.        
    
    Created By: Jake Walker
    Created Date: 12/8/2016
"""

from cs50 import SQL
import sqlite3
import datetime
from ScraperTemplates.CommonScraper import MAX_AGE_BEFORE_DEACTIVATE

# Point database to the teas.db sqlite database.
DB = SQL("sqlite:///teas.db")


def convert_boolean_to_db_bool(value):
    """Reformats boolean fields from a Python True/False to a one or zero representing SQLite database booleans."""
    if value:
        return 1
    return 0


def db_now():
    """
        Helper function to insert current date into sqlite database.  
        Sqlite datetime fields are stored in text so this normalizes the input string format:
            2.2: https://www.sqlite.org/datatype3.html
    """
    
    return datetime.datetime.strftime(datetime.datetime.now(), "%Y-%m-%d %H:%M:%S")


class ProductDB:
    """Class object to represent a product and insert it into the respective database tables"""
    def __init__(self, tea_name, tea_type, tea_description, source_name, product_id, cost, url, image_url, update_date=db_now()):
        self.tea_id = insert_update_tea_name(tea_name, tea_type, tea_description)
        self.tea_name = tea_name
        self.tea_type = tea_type
        self.tea_description = tea_description
        self.source_name = source_name
        self.product_id = product_id
        self.cost = cost
        self.url = url
        self.image_url = image_url
        self.update_date = update_date
        
        # Insert/Update the product at instantiation.
        insert_update_product(self.tea_name, self.tea_type, self.tea_description, self.source_name, self.product_id, 
                self.cost, self.url, self.image_url, self.update_date)
        
        
def get_tea_types():
    """Query to select all product classifications"""
    data = DB.execute("""
        SELECT TeaType 
        FROM TeaTypes"""
        )
    return [row["TeaType"] for row in data]


def get_tea_types_by_type(tea_type):
    """Query to select all products of a given classification"""
    data = DB.execute("""
        SELECT ID
        FROM TeaTypes
        WHERE (TeaType = :teatype)"""
        , teatype=tea_type
        )
        
    # Return the db value if collected else return None.  Assume only one ID per product classification per database restriction.
    if len(data) > 0:
        return data[0]["ID"]
    return None


def get_tea_sources_by_name(source_name):
    """Query to select all products from a given datasource"""
    data = DB.execute("""
        SELECT ID
        FROM Sources
        WHERE (SourceName = :sourcename)"""
        , sourcename=source_name
        )
    
    # Return the db value if collected else return None.  Assume only one ID per source name per database restriction.
    if len(data) > 0:
        return data[0]["ID"]
    return None


def get_tea_by_source_product(source_name, product_id):
    data = DB.execute("""
        SELECT ID, TeaID
        FROM TeasSources
        WHERE
                SourceID = :sourceid
            AND ProductID = :productid
        """
        , productid=product_id, sourceid=get_tea_sources_by_name(source_name)
        )
    
    # Return None if no data pulled from db, else return the data table.
    if len(data) > 0:
        return data
    return None


def get_teas_by_name(name):
    data = DB.execute("""
        SELECT ID
        FROM Teas
        WHERE Name = :teaname
        """
        , teaname = name
        )
    
    # Return the db value if collected else return None.  Assume only one ID per product name per database restriction.
    if len(data) > 0:
        return data[0]["ID"]
    return None


def get_teas_active():
    data = DB.execute("""
        SELECT ID, LastUpdatedDate
        FROM TeasSources
        WHERE IsAvailable = 1
        """
        )
    
    # Convert datetime string into Python datetime
    for tea in data:
        tea["LastUpdatedDate"] = datetime.datetime.strptime(tea["LastUpdatedDate"], "%Y-%m-%d %H:%M:%S")
    
    # Return the db value if collected else return None.  Assume only one ID per product name per database restriction.
    if len(data) > 0:
        return data
    return None


def insert_update_tea_name(name, tea_type, description):
    """Given a product and details, create if doesn't exist or update if does exist."""
    
    # Attempt to gather details of the product to see if it exists.
    tea_id = get_teas_by_name(name)
    type_id = get_tea_types_by_type(tea_type)
    
    # If the type does not yet exist, require it be created first.
    if not type_id:
        return RuntimeError("Invalid tea type '{teatype}'.  Tea name: {name}".format(teatype=tea_type, name=name))
    
    # If already exists, update it and do not insert.
    if tea_id:
        DB.execute("""
        UPDATE Teas
        SET 
            Name = :name,
            TeaTypeID = :teatypeid,
            Description = :description,
            LastUpdatedDate = :date
        WHERE ID = :teaid
        """, teaid=tea_id, name=name, teatypeid=type_id, description=description, date=db_now()
        )
        return tea_id
    
    # Else insert a new tea and return the ID number of the new tea.
    DB.execute("""
        INSERT INTO Teas (Name, TeaTypeID, Description, LastUpdatedDate)
        VALUES(:name, :teatypeid, :description, :date)"""
        , name=name, teatypeid=type_id, description=description, 
            date=db_now()
    )
    
    return get_teas_by_name(name=name)


def insert_update_product(tea_name, tea_type, tea_description, source_name, product_id, cost, url, image_url, is_available=True):
    """Given a product, datasource, and details, create if doesn't exist or update if does exist."""
    
    # Attempt to gather details of the product to see if it exists.
    tea_id = insert_update_tea_name(tea_name, tea_type, tea_description)
    source_id = get_tea_sources_by_name(source_name)
    
    # If the type or datasource do not yet exist, require they be created first.
    if not tea_id or not source_id:
        return RuntimeError("Invalid tea type '{teatype}' or datasource '{sourcename}'.  Tea name: {name}".format(
                                    teatype=tea_type, sourcename=source_name, name=tea_name))
    
    # Attempt to gather details of the product to see if we've provioursly entered this product into our db before or not.
    tea_mapping_id = get_tea_by_source_product(source_name, product_id)
    
    # Update existing product if already exists.
    # Assume only one tea in our db per source and product, so take the first item in the list.
    if tea_mapping_id:
        tea_mapping_id = tea_mapping_id[0]["ID"]
        DB.execute("""
            UPDATE TeasSources
            SET
                TeaID = :teaid,
                ProductID = :productid,
                CostOz = :cost,
                URL = :url,
                ImageURL = :imageurl,
                IsAvailable = :isavailable,
                LastUpdatedDate = :date
            WHERE ID = :teamappingid
        """
        , teamappingid=tea_mapping_id, teaid=tea_id, productid=product_id, cost=cost, url=url, imageurl=image_url,
                isavailable=convert_boolean_to_db_bool(is_available),
                date=db_now()
        )
        return True
    
    # Else insert a new mapping
    DB.execute("""
        INSERT INTO TeasSources (TeaID, SourceID, ProductID, CostOz, URL, ImageURL, IsAvailable, LastUpdatedDate)
        VALUES(:teaid, :sourceid, :productid, :cost, :url, :imageurl, :isavailable, :date)
        """
        , teaid=tea_id, sourceid=source_id, productid=product_id, cost=cost, url=url, imageurl=image_url,
                isavailable=convert_boolean_to_db_bool(is_available),
                # date=datetime.datetime.now()
                date=db_now()
        )


def deactivate_products():
    """For any products no longer actively available on our scrapers, deactive the products from user view on the website."""
    teas_deactivate = []
    for tea in get_teas_active():
        # Add to list to deactivate if tea is older than a certain date.
        if tea["LastUpdatedDate"] < datetime.datetime.now() - datetime.timedelta(days=MAX_AGE_BEFORE_DEACTIVATE):
            teas_deactivate.append(tea["ID"])
    
    # Deactivate any teas in the list
    if len(teas_deactivate) > 0:
        for tea in teas_deactivate:
            DB.execute("""
                UPDATE TeasSources
                SET IsAvailable = 0
                WHERE ID = :teaidstr
                """, teaidstr=tea
            )


def _test(testing_db=False):
    """Testing Functions"""
    
    # Base use-cases assumed to exist:
    assumed_tea_type, assumed_tea_type_id = "Green Tea", 1      # Green Tea should be one of them (basic use-case assumption)
    assumed_tea_source, assumed_tea_source_id = "TeaSource", 1  # TeaSource is the first scraper created
    # Since we don't delete products (only deactivate them), we can assume this exists:
    assued_source, assumed_source_product, assumed_tea_name = "Camellia Sinensis", "CSTB-1", "Bai Hao Yin Zhen"
    
    # There should be multiple types of tea.  
    tea_types = get_tea_types()
    assert len(tea_types) > 0
    assert assumed_tea_type in tea_types
    assert get_tea_types_by_type(tea_type=assumed_tea_type) == assumed_tea_type_id
    
    # Assume tea sources exist.
    assert get_tea_sources_by_name(source_name=assumed_tea_source) == assumed_tea_source_id
    
    # Assume products and sources pull data
    assert get_tea_by_source_product(source_name=assued_source, product_id=assumed_source_product)
    assert get_teas_by_name(name=assumed_tea_name)
    
    if testing_db:
        """Testing function to insert into db."""
        x = ProductDB(
                tea_name="Albert Square Blend", 
                tea_type="Black Tea",
                tea_description="TESTING",
                source_name="TeaSource",
                product_id="11873637315",
                cost=5.015, 
                url="https://www.teasource.com/collections/green-tea/products/blooming-green-tea-green-tea",
                image_url = ""
                )
        print(x)
        print(insert_update_tea_name(x.tea_name, x.tea_type, x.tea_description))
        print(get_tea_by_source_product(x.source_name, x.product_id))
        result = insert_update_product(x.tea_name, x.tea_type, x.tea_description, x.source_name, x.product_id, 
                x.cost, x.url, x.image_url)
        print(result)


if __name__ == '__main__':
    _test(testing_db=False)