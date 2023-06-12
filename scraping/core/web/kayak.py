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

# Google search page class declarations

GENDER_DIV = "EA yP"
INPUT_ID = "lst-ib"
LI_CLASS = "g"

SIGNIN_A = "gb_70"

# strip html


class NoElementError(Exception):
    '''Handling not search problems - assuming didn't load'''
    pass

class MLStripper(HTMLParser):
    def __init__(self):
        self.reset()
        self.fed = []
    def handle_data(self, d):
        self.fed.append(d)
    def get_data(self):
        return ''.join(self.fed)

def strip_tags(html):
    s = MLStripper()
    s.feed(html)
    return s.get_data()

def create_connection(db_file):
    """ create a database connection to the SQLite database
        specified by db_file
    :param db_file: database file
    :return: Connection object or None
    """
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
    #    database = r"C:\sqlite\db\pythonsqlite.db"

    sql_create_search_table = """ CREATE TABLE IF NOT EXISTS search (
                                        runID text NOT NULL,
                                        blockID text NOT NULL,
                                        unitID text NOT NULL,
                                        date_ran text NOT NULL,
                                        time_ran text NOT NULL,
                                        flight_pair text NOT NULL,
                                        profile_name text NOT NULL,
                                        depart_date text NOT NULL,
                                        return_date text NOT NULL,
                                        ordering integer NOT NULL,
                                        price integer NOT NULL,
                                        url text NOT NULL,
                                        currency text NOT NULL,
                                        seller text NOT NULL,
                                        flight_class text,
                                        is_sponsered integer,
                                        depart_time text NOT NULL,
                                        depart_carrier text NOT NULL,
                                        depart_stops text NOT NULL,
                                        depart_leg_length text NOT NULL,
                                        depart_start_place text NOT NULL,
                                        depart_end_place text NOT NULL,
                                        return_time text NOT NULL,
                                        return_carrier text NOT NULL,
                                        return_stops text NOT NULL,
                                        return_leg_length text NOT NULL,
                                        return_start_place text NOT NULL,
                                        return_end_place text NOT NULL,
                                        secondary_ordering text NOT NULL,
                                        PRIMARY KEY (runID, blockID, time_ran, flight_pair, profile_name, depart_date, return_date, ordering, secondary_ordering)
                                        )"""
    sql_create_ad_table = """ CREATE TABLE IF NOT EXISTS ads (
                                        runID text NOT NULL,
                                        blockID text NOT NULL,
                                        unitID text NOT NULL,
                                        date_ran text NOT NULL,
                                        time_ran text NOT NULL,
                                        flight_pair text NOT NULL,
                                        profile_name text NOT NULL,
                                        depart_date text NOT NULL,
                                        return_date text NOT NULL,
                                        ordering integer NOT NULL,
                                        url text NOT NULL,
                                        description text NOT NULL,
                                        price text,
                                        brand text,
                                        inline_data NOT NULL,
                                        PRIMARY KEY (runID, blockID, time_ran, flight_pair, profile_name, ordering, depart_date, return_date)
                                        )"""
    # create a database connection
    conn = create_connection(database)
    # create tables
    if conn is not None:
        # create projects table
        create_table(conn, sql_create_search_table)
        # create tasks table
        create_table(conn, sql_create_ad_table)
    else:
        print("Error! cannot create the database")


class KayakUnit(browser_unit.BrowserUnit):
    '''The main kayak unit. Functions similar to browser unit but dumps data into sql'''

    def __init__(self, browser, log_file, unit_id, treatment_id, headless=True, proxy=None, block_id = None):
        '''Same setup as standard browser units'''
        browser_unit.BrowserUnit.__init__(self, browser, log_file, unit_id, treatment_id, headless, proxy=proxy, block_id = block_id)

    def insert_into_db(self, database_name, search_result, ad_result):
        '''INserting reserach of search and ads into the database'''
        db = sqlite3.connect(database_name)
        curr = db.cursor()
        try:
            if len(search_result):
                columns = ', '.join(search_result[0].keys())
                placeholders = ':'+', :'.join(search_result[0].keys())
                query = 'INSERT INTO search (%s) VALUES (%s)' % (columns, placeholders)
                curr.executemany(query, search_result)

            if len(ad_result):
                columns = ', '.join(ad_result[0].keys())
                placeholders = ':'+', :'.join(ad_result[0].keys())
                query = 'INSERT INTO ads (%s) VALUES (%s)' % (columns, placeholders)
                curr.executemany(query, ad_result)

            db.commit()
            db.close()
            self.log('trasaction', 'something', 'added into db')
        except Error as e:
            self.log('error', "base", "couldn't add to the database %e" % str(e))

    def read_inner_list(self, base):
        '''Sometimes Kayak serach results have a dropdown to collect even more
         results for the same flight (multiple sellers). This handles that web
         element'''
        res = []
        inner_base = base.find_elements_by_xpath(".//ul[@class = 'option-list']")
        if len(inner_base):
            inner_base = inner_base[0]
            prices = inner_base.find_elements_by_xpath(".//span[@class = 'price-text']")
            provider = inner_base.find_elements_by_xpath(".//span[contains(@class, 'providerName option-text')]")
            if(len(prices) != len(provider)):
                print("Not matching up ignoring")
                return(res)
            prices_arr = [x.get_attribute('innerHTML').strip().strip("\n") for x in prices]
            provider_arr = [x.get_attribute('innerHTML').strip("\n").strip() for x in provider]
            for i in range(0, len(prices_arr)):
                temp = OrderedDict()
                price = prices_arr[i]
                temp['currency'] = price
                temp['seller'] = provider_arr[i]
                try:
                    temp['price'] = int(price.replace("$", '').replace(",", "").split("\n")[0]) * 100 #Remove formatting and get it in cents
                except ValueError:
                    print("No price displayed - setting it to -1")
                    temp['price'] = -1
                temp['secondary_ordering'] = i + 1
                res.append(temp)
        return(res)


    def read_results(self, db_name, run_id, flight_pair, depart_date, return_date):
        '''Main read results. Crawls through page and takes the first page of ressults'''
        attempt = 0
        completed = False
        while attempt < 3 and not completed:
            search_result = [] # 'native' search
            ad_result = [] # ads we see
            webdriver = self.driver
            try:
                # Handle the popup that shows up sometimes
                xpath = '//*[contains(@id, "dialog-content")]/*[contains(@id, "dialog-close")]'
                for el in webdriver.find_elements_by_xpath(xpath):
                    if el.is_displayed():
                        el.click()

                    # Get the search results to start narrowing down
                try:
                    page = webdriver.find_element_by_xpath('//div[@id="searchResultsList"]')
                except NoSuchElementException:
                    raise NoElementError("Can't find search result list")

                now = datetime.now()
                date = now.date()

                # add the using an ordered dict so that the order stays
                # consistent when adding to db
                # common_params = [(key, val) for key,val in self.params.items()]
                common_info = OrderedDict()
                common_info.update({'flight_pair': flight_pair, 'depart_date' : depart_date, 'return_date' : return_date})
                common_info.update({'url': webdriver.current_url, 'time_ran' : str(now), "runID" : run_id, "blockID": self.block_id, "unitID" : self.unit_id, 'date_ran' : str(date), 'profile_name' : self.treatment_id })

                # Get all the search results and process them
                arr = page.find_elements_by_xpath(".//div[@class='resultWrapper']")
                for count, item in enumerate(arr):
                    info = OrderedDict()
                    # print("Search on count %d with attempt %d and completed = %s"  % (count, attempt, str(completed)) )
                    # Depature leg and return leg respectively
                    top = item.find_element_by_xpath(".//li[@class = 'flight with-gutter']")
                    bottom = item.find_element_by_xpath(".//li[@class = 'flight ']")
                    temp = {'depart': top, 'return': bottom}
                    for name, elem in temp.items():
                        section_times = elem.find_element_by_xpath(".//div[@class = 'section times']")
                        try:
                            time_length = section_times.find_element_by_xpath(".//div[@class = 'top']")
                        except NoSuchElementException:
                            raise NoElementError("Can't find top")
                        carrier = section_times.find_element_by_xpath(".//div[contains(@class, 'bottom ')]")
                        info[name + '_time'] = time_length.text
                        info[name + '_carrier'] = carrier.text
                        section_stops = elem.find_element_by_xpath(".//div[@class = 'section stops']").text
                        info[name + '_stops'] = section_stops
                        section_duration = elem.find_element_by_xpath(".//div[contains(@class, 'section duration')]").text
                        section_duration = section_duration.split("\n")
                        info[name + '_leg_length'] = section_duration[0]
                        info[name + '_start_place'] = section_duration[1]
                        info[name + '_end_place'] = section_duration[-1]
                    # Handle getting pricing info
                    info['ordering'] = count + 1
                    info.update(common_info)
                    pricing_info = item.find_elements_by_xpath(".//a[contains(@id, 'booking-link')]")
                    try:
                        info['flight_class'] = pricing_info[3].text
                    except (IndexError, NoSuchElementException):
                        info['flight_class'] = ''
                    # Check if this is sponsered or not
                    try:
                        is_sponsered = item.find_element_by_xpath(".//div[@class = 'section fsp']").text
                        info['is_sponsered'] = int(bool(is_sponsered))
                    except NoSuchElementException:
                        info['is_sponsered'] = 0

                    '''Get the other potential sellers'''
                    other_list = self.read_inner_list(item)
                    for elem in other_list:
                        elem.update(info)
                        search_result.append(elem)

                    '''Get the base sellers'''
                    price = pricing_info[0].text
                    try:
                        # Remove formatting and get it in cents
                        info['price'] = int(price.replace("$", '').replace(",", "").split("\n")[0]) * 100
                    except ValueError:
                        print("No price displayed - setting it to -1")
                        info['price'] = -1
                    info['currency'] = price
                    info['seller'] = pricing_info[1].text
                    info['secondary_ordering'] = 0
                    # Combine specific and common info together
                    search_result.append(info)

                # Handling embeeded ads
                ads = page.find_elements_by_xpath(".//div[contains(@onclick, 'inline.ad')]")
                for count, ad in enumerate(ads):
                    #print("Ad on count %d with attempt %d and completed = %s"  % (count, attempt, str(completed)) )
                    info = OrderedDict()
                    try:
                        info['description'] = ad.find_element_by_xpath(".//div[@class = 'inlineAdDescription']").text
                    except NoSuchElementException:
                        info['description'] = ""
                    info['ordering'] = count + 1
                    # Not all ad have prices - handle them if they do
                    try:
                        info['price'] = ad.find_element_by_xpath(".//div[@class = 'price']").text
                        info['brand'] = ad.find_element_by_xpath(".//div[@class = 'provider-brand']").text
                    except NoSuchElementException:
                        info['price'] = ""
                        info['brand'] = ""
                    try:
                        info['inline_data'] = ad.find_element_by_xpath(".//li[@class = 'inlineAdPriceRow ']").text
                    except NoSuchElementException:
                        info['inline_data'] = ad.find_element_by_xpath(".//div[@class = 'inlineAdFooter clean']").text
                    info.update(common_info)
                    ad_result.append(info)
                completed = True

            except (StaleElementReferenceException, NoElementError) as e:
                print("retrying from stale element or no element errror exception on webpage %s" % str(self.driver.current_url))
                print(e)
                self.driver.refresh()
                time.sleep(30)
                attempt += 1

        if completed == False:
            print("Failed to updated - please rerun")
            return
        else:
            table_create(db_name)
            print("Inserted into database")
            self.insert_into_db(db_name, search_result, ad_result)
