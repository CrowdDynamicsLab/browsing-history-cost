import time, re                                                     # time.sleep, re.split
import sys                                                          # some prints
import sqlite3

from selenium import webdriver                                      # for running the driver on websites
from datetime import datetime                                       # for tagging log with datetime
from selenium.webdriver.common.keys import Keys                     # to press keys on a webpage
from . import browser_unit
from selenium.webdriver import Firefox
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException, StaleElementReferenceException
from datetime import datetime
from sqlite3 import Error
from collections import OrderedDict
from html.parser import HTMLParser


from urllib.parse import urlparse
from urllib.parse import parse_qs

class NoElementError(Exception):
    '''Handling not search problems - assuming didn't load.'''

    pass

class CaptchaFound(Exception):
    '''When captcha's appear.'''
    pass


class NotMatchingStar(Exception):
    '''When captcha's appear.'''
    pass


def create_connection(db_file):
    """ create a database connection to the SQLite database.
    :param db_file: database file
    :return: Connection object or None"""
    conn = None
    try:
        conn = sqlite3.connect(db_file)
        return conn
    except Error as e:
        print(e)
        return conn


def create_table(conn, create_table_sql):
    """ create a table from the create_table_sql statement
   :param conn: Connection object
   :param create_table_sql: a CREATE TABLE statement
   :return:
    """
    try:
        c = conn.cursor()
        c.execute(create_table_sql)
    except Error as e:
        print(e)


def table_create(db_file):
    database = db_file
    sql_create_search_table = """ CREATE TABLE IF NOT EXISTS hotel_prices (
                                        runID text NOT NULL,
                                        blockID text NOT NULL,
                                        unitID text NOT NULL,
                                        date_ran text NOT NULL,
                                        time_ran text NOT NULL,
                                        profile_name text NOT NULL,
                                        city text NOT NULL,
                                        checkin_date text NOT NULL,
                                        checkout_date text NOT NULL,
                                        base_search_url text NOT NULL,
                                        price integer NOT NULL,
                                        hotel_id text,
                                        hotel_name text NOT NULL,
                                        num_stars integer,
                                        address text NOT NULL,
                                        hotel_url text NOT NULL,
                                        result_ordering integer NOT NULL,
                                        currency text NOT NULL,
                                        seller text NOT NULL,
                                        amenities text,
                                        page_url text NOT NULL,
                                        room_configuration text NOT NULL,
                                        row_ordering integer NOT NULL,
                                        seller_ordering integer NOT NULL,
                                        review_score text,
                                        PRIMARY KEY (runID, blockID, date_ran, time_ran, city, profile_name, checkin_date, checkout_date, result_ordering, row_ordering, seller_ordering)
                                        )"""
    # create a database connection
    conn = create_connection(database)
    # create tables
    if conn is not None:
        # create projects table
        create_table(conn, sql_create_search_table)
    else:
        print("Error! cannot create the database")


def table_create_macy(db_file):
    database = db_file
    sql_create_search_table = """ CREATE TABLE IF NOT EXISTS macy_prices_direct (
                                        runID text NOT NULL,
                                        blockID text NOT NULL,
                                        unitID text NOT NULL,
                                        date_ran text NOT NULL,
                                        time_ran text NOT NULL,
                                        profile_name text NOT NULL,
                                        macy_id text NOT NULL,
                                        product_name text,
                                        currency text NOT NULL,
                                        price integer NOT NULL,
                                        page_url text NOT NULL,
                                        PRIMARY KEY (runID, blockID, date_ran, time_ran, profile_name, macy_id)
                                        )"""
    conn = create_connection(database)
    # create tables
    if conn is not None:
        # create projects table
        create_table(conn, sql_create_search_table)
    else:
        print("Error! cannot create the database")

def table_create_macy_search(db_file):
    database = db_file
    sql_create_search_table = """ CREATE TABLE IF NOT EXISTS macy_prices_search (
                                        runID text NOT NULL,
                                        blockID text NOT NULL,
                                        unitID text NOT NULL,
                                        date_ran text NOT NULL,
                                        time_ran text NOT NULL,
                                        profile_name text NOT NULL,
                                        search_category text NOT NULL,
                                        search_url text NOT NULL,
                                        product_url text NOT NULL,
                                        product_id text NOT NULL,
                                        product_name text,
                                        brand_name text,
                                        is_sponsored int NOT NULL,
                                        currency text NOT NULL,
                                        price integer NOT NULL,
                                        ordering integer NOT NULL,
                                        PRIMARY KEY (runID, blockID, date_ran, time_ran, profile_name, product_id, ordering)
                                        )"""
    conn = create_connection(database)
    # create tables
    if conn is not None:
        # create projects table
        create_table(conn, sql_create_search_table)
    else:
        print("Error! cannot create the database")

def insert_into_db_inner(database_name, search_result, table_name):
    """Inserting results of hotel search into the database."""
    db = sqlite3.connect(database_name)
    curr = db.cursor()
    if len(search_result):
        columns = ', '.join(search_result[0].keys())
        placeholders = ':' + ', :'.join(search_result[0].keys())
        query = 'INSERT INTO %s (%s) VALUES (%s)' % (table_name, columns, placeholders)
        print(query)
        print(search_result[0])
        curr.executemany(query, search_result)

        db.commit()
        db.close()

def clean_price(price):
    """Clean the price string to an int."""
    return(int(float(price.replace("$", '').replace(",", "").split("\n")[0]) * 100))


class MacyProducts(browser_unit.BrowserUnit):
    def __init__(self, browser, log_file, unit_id, treatment_id, headless=True, proxy=None, block_id = None):
        '''Same setup as standard browser units.'''
        browser_unit.BrowserUnit.__init__(self, browser, log_file, unit_id, treatment_id, headless, proxy=proxy, block_id = block_id)

    def read_results(self, db_name, runID):
        # Assume you're already on the page
        try:
            self.log('base', 'looking out', 'wtf')
            print("getting product names")
            now = datetime.now()
            date = now.date()
            try:
                product_name = self.driver.find_element_by_xpath("//div[@data-auto='product-name']").get_attribute('innerHTML').strip()
            except NoSuchElementException as e:
                print("Can't find product name - setting it to empty")
                product_name = ""
            product_price_str = self.driver.find_element_by_xpath("//div[@class = 'lowest-sale-price']").text.strip()
            price_int = clean_price(product_price_str)
            curr_url = self.driver.current_url
            parsed_url = urlparse(curr_url)
            self.log('base', 'looking out', 'wtf')
            print("trying parse")
            item_id = parse_qs(parsed_url.query)['ID'][0]
            common_info = OrderedDict()
            common_info.update({'page_url': curr_url, 'time_ran': str(now), "runID": runID, "blockID": self.block_id, "unitID": self.unit_id, 'date_ran': str(date), 'profile_name': self.treatment_id})
            common_info.update({'macy_id': item_id, 'product_name': product_name, 'currency': product_price_str, 'price': price_int})
            print("try to creeate table")
            self.log('base', 'looking out', 'wtf')
            table_create_macy(db_name)
            self.insert_into_db(db_name, [common_info])

        except NoSuchElementException as e:
            msg = "couldn't find price or product %s" % str(e)
            print(msg)
            self.log("error", 'base', msg)

    def insert_into_db(self, database_name, search_result):
        """Inserting results of hotel search into the database."""
        try:
            insert_into_db_inner(database_name, search_result, 'macy_prices_direct')
            self.log('trasaction', 'added into db', self.driver.current_url)
        except Error as e:
            self.log('error', "base", "couldn't add to the database %s" % str(e))
            raise(e)

class MacySearch(browser_unit.BrowserUnit):
    def __init__(self, browser, log_file, unit_id, treatment_id, headless=True, proxy=None, block_id = None):
        '''Same setup as standard browser units.'''
        browser_unit.BrowserUnit.__init__(self, browser, log_file, unit_id, treatment_id, headless, proxy=proxy, block_id = block_id)

    def insert_into_db(self, database_name, search_result):
        """Inserting results of hotel search into the database."""
        try:
            insert_into_db_inner(database_name, search_result, 'macy_prices_search')
            self.log('trasaction', 'added into db', self.driver.current_url)
        except Error as e:
            self.log('error', "base", "couldn't add to the database %s" % str(e))
            raise(e)

    def read_results(self, db_name, runID, product_set):
        # Assume you're already on the page
        try:
            self.log('base', 'looking out', 'wtf')
            print("getting product names")
            driver = self.driver
            all_products_info = driver.find_elements_by_xpath("//li[@class = 'cell productThumbnailItem']")
            product_results = []
            common_info = OrderedDict()
            curr_url = self.driver.current_url
            now = datetime.now()
            date = now.date()

            common_info.update({'search_url': curr_url, 'time_ran': str(now), "runID": runID, "blockID": self.block_id, "unitID": self.unit_id, 'date_ran': str(date), 'profile_name': self.treatment_id, 'search_category': product_set})

            for i, p in enumerate(all_products_info):
                try:
                    product = p.find_element_by_xpath(".//div[@class = 'productDescription']")
                    hyperlink_elem = product.find_element_by_tag_name('a')
                    next_url = hyperlink_elem.get_attribute('href')
                    product_name = hyperlink_elem.get_attribute('title')
                    product_id = parse_qs(urlparse(next_url).query)["ID"][0]
                    brand_name = hyperlink_elem.find_element_by_xpath(".//div[@class = 'productBrand']").text
                    try:
                        price_info = product.find_element_by_xpath(".//span[@class = 'discount']").text
                    except NoSuchElementException:
                        price_info = product.find_element_by_xpath(".//span[@class = 'regular']").text

                    price_info = price_info.split("$")[-1]
                    price_int = clean_price(price_info)
                    sponsored = False
                    try:
                        p.find_element_by_xpath(".//div[@class = 'sponsored-items-label']")
                        sponsored = True
                    except NoSuchElementException:
                        sponsored = False

                    prod_dict = {'product_url': next_url, 'product_id': product_id, 'product_name': product_name, 'brand_name' : brand_name, 'currency': price_info, 'price': price_int, 'is_sponsored': int(sponsored), 'ordering' : i}
                    to_add = OrderedDict()
                    to_add.update(prod_dict)
                    to_add.update(common_info)
                    product_results.append(to_add)
                except NoSuchElementException:
                    print("Passing")
                    pass
                # print("try to creeate table")
                # self.log('base', 'looking out', 'wtf')
            table_create_macy_search(db_name)
            self.insert_into_db(db_name, product_results)
        except Exception as e:
            print("Couldn't finish check")
            print(e)
            raise(e)

class KayakHotels(browser_unit.BrowserUnit):
    """The main kayak unit. Functions similar to browser unit but dumps data into sql."""

    def __init__(self, browser, log_file, unit_id, treatment_id, headless=True, proxy=None, block_id = None):
        '''Same setup as standard browser units.'''
        browser_unit.BrowserUnit.__init__(self, browser, log_file, unit_id, treatment_id, headless, proxy=proxy, block_id = block_id)

    def insert_into_db(self, database_name, search_result):
        """Inserting results of hotel search into the database."""
        try:
            insert_into_db_inner(database_name, search_result, 'hotel_prices')
            self.log('trasaction', 'added into db', self.driver.current_url)
        except Error as e:
            self.log('error', "base", "couldn't add to the database %s" % str(e))
            raise(e)

    def read_results(self, db_name, runID, city, checkin_date, checkout_date, star_target):
        """Main read results. Crawls through page and a set of results."""
        attempt = 0
        completed = False
        while attempt < 3 and not completed:
            search_result = [] # 'native' search
            webdriver = self.driver
            try:
                # Handle the popup that shows up sometimes
                xpath = '//*[contains(@id, "dialog-content")]/*[contains(@id, "dialog-close")]'
                for el in webdriver.find_elements_by_xpath(xpath):
                    if el.is_displayed():
                        el.click()

                now = datetime.now()
                date = now.date()

                arr = webdriver.find_elements_by_xpath(".//div[@class = 'FLpo-hotel-name']")
                num_hotels = len(arr)
                if num_hotels == 0:
                    print("Can't find anything check if it executed and there isn't any option")
                    # Check if the header says there's no matching hotel (indictaing there really is no hotels. If the element fails
                    # to be found or that text doesn't show up reset like normal)
                    try:
                        to_check = webdriver.find_element_by_xpath("//div[@class= 'title']")
                        print(to_check.text)
                        if to_check and "No matching" in to_check.text:
                            self.log("Meta",  "No results", "No search results found this query - exit")
                            print("No actual search results - end here")
                            completed = True
                            break
                        else:
                            print("Couldn't find a element type?")
                            print(to_check.text)
                            # Reset by raising the relevant exception
                            raise NoSuchElementException
                    except NoSuchElementException as e:
                        # Reset by raising the relevant exception
                        print("Failed finding it? ")
                        print(str(e))
                        raise NoSuchElementException

                # add the using an ordered dict so that the order stays
                # consistent when adding to db
                # common_params = [(key, val) for key,val in self.params.items()]
                common_info = OrderedDict()
                common_info.update({'city': city, 'checkin_date': checkin_date, 'checkout_date': checkout_date})
                common_info.update({'base_search_url': webdriver.current_url, 'time_ran': str(now), "runID": runID, "blockID": self.block_id, "unitID": self.unit_id, 'date_ran': str(date), 'profile_name': self.treatment_id})

                base_window = webdriver.current_window_handle
                curr_window = None
                search_range = min(num_hotels, 5)
                for i in range(search_range):
                    inner_complete = False
                    captcha_found = False
                    num_attempts_inner = 0
                    print("On %d out of %d" % (i + 1, search_range))
                    self.log("Event", "Loop info", "On event %d out of %d" % (i + 1, search_range))

                    arr[i].click()
                    chwd = webdriver.window_handles
                    for w in chwd:
                        if(w != base_window):
                            print("Changed windows")
                            webdriver.switch_to.window(w)
                            curr_window = w

                    while(num_attempts_inner < 3 and not inner_complete and not captcha_found):
                        print("On attempt %d" % (num_attempts_inner + 1))
                        num_attempts_inner += 1
                        try:
                            # This swiches tab automatially

                            if 'security' in webdriver.current_url:
                                raise CaptchaFound()
                            print("Clicked through to hotel\n")
                            print("Driver title: " + webdriver.title)
                            time.sleep(10)
                            more_base = OrderedDict()
                            try:
                                hotel_name = webdriver.find_element_by_xpath(".//h1[@class = 'c3xth-hotel-name']")
                            except NoSuchElementException:
                                continue

                            print(hotel_name.text)
                            more_base['hotel_name'] = hotel_name.text

                            #star_element = webdriver.find_element_by_xpath("//div[@class='c3xth-stars-in-title']")
                            try:
                                star_element = webdriver.find_element_by_xpath("//div[@class='c3xth-stars-in-title']")
                                num_stars = len(star_element.find_elements_by_xpath(".//span[@class='O3Yc-star O3Yc-mod-black-active']"))
                                print("NUM STARS: " + str(num_stars))
                            except NoSuchElementException:
                                print("Can't find star into might be zero")
                                num_stars = 0
                            if num_stars != star_target or (star_target == 0 and num_stars >= 2):
                                raise NotMatchingStar()
                            address = webdriver.find_element_by_class_name("c3xth-address")
                            more_base['num_stars'] = num_stars
                            more_base['address'] = address.text

                            hotel_page_url = webdriver.current_url
                            more_base['hotel_url'] = hotel_page_url
                            more_base['result_ordering'] = i
                            try:
                                # The URLs seem to have some sembalance of a hotelid. Attempt to grab it
                                hotel_id = "-".join(hotel_page_url.split(checkin_date)[0].split("-")[-3:-1])
                                more_base['hotel_id'] = hotel_id
                                print("Hotel id %d" % hotel_id)
                            except Exception:
                                pass
                            try:
                                review_score = webdriver.find_element_by_class_name("l3xK-reviews-summary-score")
                                more_base['review_score'] = review_score.text
                                print("Review score: " + review_score.text)

                            except NoSuchElementException:
                                print("No review score for this object")
                                more_base['review_score'] = None
                            all_rows = webdriver.find_elements_by_class_name("I937-rates-row")
                            for j, row in enumerate(all_rows):
                                base_dict = {}
                                room_configuration = row.find_element_by_xpath(".//div[@class = 'c5l3f-accommodation-type']").text
                                amenities = row.find_elements_by_xpath(".//div[@class = 'c5l3f-freebies']")
                                if (len(amenities)):
                                    base_dict['amenities'] = amenities[0].text
                                else:
                                    print("no amenities")
                                    base_dict['amenities'] = ""

                                base_dict['room_configuration'] = room_configuration
                                base_dict['page_url'] = webdriver.current_url
                                base_dict['row_ordering'] = j
                                per_dict = OrderedDict()
                                seller_main = row.find_element('tag name', 'img').get_attribute('alt')
                                price_main = row.find_element_by_class_name('c5l3f-price-col').text
                                per_dict['seller'] = seller_main
                                per_dict['currency'] = price_main
                                try:
                                    per_dict['price'] = clean_price(price_main)
                                except ValueError:
                                    print("No price displayed - setting it to -1")
                                    per_dict['price'] = -1

                                per_dict['seller_ordering'] = 0
                                to_add = OrderedDict()
                                to_add.update(more_base)
                                to_add.update(base_dict)
                                to_add.update(per_dict)
                                to_add.update(common_info)
                                search_result.append(to_add)
                                additional_prices = row.find_elements_by_css_selector("[aria-label='View more deals']")
                                if len(additional_prices):
                                    additional_prices[0].click()
                                    # get the dropdown elements
                                    droplist = additional_prices[0].find_elements_by_xpath("//div[@class = 'Snmu-dropdown-list']")
                                    if len(droplist):
                                        menuitems = droplist[0].find_elements_by_xpath("//div[@role='menuitem']")
                                        # If there's even more in the dropdown have to go with a javascript click instead of a direct seleinum click
                                        if len(menuitems) and len(menuitems[-1].find_elements_by_xpath("//div[@class = 'Snmu-more-options']")):
                                            webdriver.execute_script("arguments[0].click();", menuitems[-1])
                                            menuitems = droplist[0].find_elements_by_xpath("//div[@role='menuitem']")
                                        for k, elem in enumerate(menuitems):
                                            per_dict = OrderedDict()
                                            try:
                                                second_provider = elem.find_element_by_xpath(".//span[@class = 'Snmu-provider']").text
                                                second_price = elem.find_element_by_xpath("//span[@class = 'Snmu-price ']").text
                                                per_dict['seller'] = second_provider
                                                per_dict['currency'] = second_price
                                                try:
                                                    per_dict['price'] = clean_price(second_price)
                                                except ValueError:
                                                    print("Couldn't parse the price set to -1")
                                                    per_dict['price'] = -1
                                                per_dict['seller_ordering'] = k + 1
                                                to_add = OrderedDict()
                                                to_add.update(more_base)
                                                to_add.update(base_dict)
                                                to_add.update(per_dict)
                                                to_add.update(common_info)
                                                search_result.append(to_add)
                                            except NoSuchElementException:
                                                print("Couldn't find anything - double check?")
                                                print(elem.get_attribute('outerHTML'))
                                        # Reset the location
                                    additional_prices[0].click()
                            inner_complete = True
                        except CaptchaFound as e:
                            self.log("Meta",  "CAPTCHA", "Captcha found")

                            print("CaptchaFound - skipping this one")
                            captcha_found = True
                        except NotMatchingStar as e:
                            print("No star found go to the next thing")
                            self.log("Meta",  "Star Info", "Star not matching the query we're looking for")
                            break
                        except (StaleElementReferenceException, NoSuchElementException, NoSuchElementException) as e:
                            print("retrying from stale element or no element errror exception on webpage %s" % str(self.driver.current_url))
                            print(e)
                            self.driver.refresh()
                            time.sleep(5)
                            num_attempts_inner += 1

                    if captcha_found and inner_complete:
                        raise Exception("Something went wrong")
                    if captcha_found:
                        print("Captcha found skipping ")
                    elif inner_complete:
                        print("Successfully finished this one")
                    else:
                        print("Something else might have went wrong check error")

                    print("Switching base to base window")
                    webdriver.close()
                    webdriver.switch_to.window(base_window)
                    time.sleep(60)

                completed = True
            except (StaleElementReferenceException, NoElementError, NoSuchElementException) as e:
                print("retrying from stale element or no element errror exception on webpage %s" % str(self.driver.current_url))
                print(e)
                self.driver.refresh()
                time.sleep(30)
                attempt += 1

        if not completed and not len(search_result):
            print("Failed to updated - either no results or an error - please check logs and rerun if necessary")
            return
        elif len(search_result) and not completed:
            self.log("Meta", 'Things to add', "adding results but might not have all reuslts")
            table_create(db_name)
            self.insert_into_db(db_name, search_result)
        else:
            table_create(db_name)
            self.insert_into_db(db_name, search_result)
