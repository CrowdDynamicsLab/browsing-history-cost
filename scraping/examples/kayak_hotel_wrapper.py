import sys, os
sys.path.append("../core")          # files from the core
import adfisher                     # adfisher wrapper function
import web.pre_experiment.alexa     # collecting top sites from alexa
import web.kayak_hotels               # collecting ads
import time
import sqlite3
from sqlite3 import Error



def create_treatment_dict():
    '''Create mapping (need to tdo this manually to avoid scoping) issues'''
    dic_treatment = {
    'control': control_treatment,
    'female': lambda unit: exp_treatment_wrapper(unit, 'female'),
    'male': lambda unit: exp_treatment_wrapper(unit, 'male'),
    'youth': lambda unit: exp_treatment_wrapper(unit, '18-34'),
    'senior': lambda unit: exp_treatment_wrapper(unit, 'over65'),
    'female_panagotis': lambda unit: exp_treatment_wrapper(unit, 'women_panogotis'),
    'male_panagotis': lambda unit: exp_treatment_wrapper(unit, 'men_panogotis'),
    'youth_panagotis': lambda unit: exp_treatment_wrapper(unit, 'youth_panogotis'),
    'senior_panagotis': lambda unit: exp_treatment_wrapper(unit, 'senior_panogotis'),
    'middle_age': lambda unit: exp_treatment_wrapper(unit, '55-64'),
    'african_american': lambda unit: exp_treatment_wrapper(unit, 'african_american'),
    'asian': lambda unit: exp_treatment_wrapper(unit, 'asian'),
    'caucasian': lambda unit: exp_treatment_wrapper(unit, 'caucasian'),
    'hispanic': lambda unit: exp_treatment_wrapper(unit, 'hispanic')
    }
    return(dic_treatment)

def make_browser(unit_id, treatment_id, log_file, block_id = None):
    b = web.kayak_hotels.KayakHotels(log_file=log_file, unit_id=unit_id,
        treatment_id=treatment_id, headless=False, browser="firefox", block_id = block_id)
    return b


def make_browser_macy(unit_id, treatment_id, log_file, block_id = None):
    b = web.kayak_hotels.MacyProducts(log_file=log_file, unit_id=unit_id,
        treatment_id=treatment_id, headless=False, browser="firefox", block_id = block_id)
    return b

def make_browser_macy_search(unit_id, treatment_id, log_file, block_id = None):
    b = web.kayak_hotels.MacySearch(log_file=log_file, unit_id=unit_id,
        treatment_id=treatment_id, headless=False, browser="firefox", block_id = block_id)
    return b
# Control Group treatment (blank)
def control_treatment(unit):
    pass

# Experimental Group treatment wrapper
def exp_treatment_wrapper(unit, name):
	fname = "%s.txt" % name
	f_path = os.path.join('site_files', fname)
	unit.visit_sites(f_path)

# Measurement - Collects ads
# checks all the sites that adfisher could previously collect on
# (~10 minutes for src and href)
def measurement(unit, city, checkin_date, checkout_date, runID, db_location):
	# 1 guest, 5 stars, sort by price low-to-high
  filters = "/1adults?fs=stars=*5&sort=price_a"
  stars = [5, 4, 3, 2, 0]
  print("working on city %s" % city)
  for star in stars:
    print("Working on star %d" % star)
    if star != 0:
      filters = "/1adults?fs=stars=*%d&sort=price_a" % star
    else:
      filters = "/1adults?sort=price_a"
    search = "https://www.kayak.com/hotels/%s/%s/%s%s" % (city, checkin_date, checkout_date, filters)
    unit.driver.get(search)
    time.sleep(10)
    unit.read_results(db_location, runID, city, checkin_date, checkout_date, star)


def measurement_recommended(unit, city, checkin_date, checkout_date, runID, db_location):
  # 1 guest, 5 stars, sort by price low-to-high
  filters = "/1adults?fs=stars=*5&sort=rank_a"
  stars = [5, 4, 3, 2, 0]
  print("working on city %s" % city)
  for star in stars:
    print("Working on star %d" % star)
    if star != 0:
      filters = "/1adults?fs=stars=*%d&sort=rank_a" % star
    else:
      filters = "/1adults?sort=rank_a"
    search = "https://www.kayak.com/hotels/%s/%s/%s%s" % (city, checkin_date, checkout_date, filters)
    unit.driver.get(search)
    time.sleep(10)
    unit.read_results(db_location, runID, city, checkin_date, checkout_date, star)

def measurement_macy(unit, fname, runID, db_location):
  unit.log("Trying", 'to', 'measure')
  with open(fname) as fp:
    for url in fp:
      print("Working on url %s" % url)
      unit.driver.get(url)
      time.sleep(5)
      unit.read_results(db_location, runID)

def measurement_macy_search(unit, url, search_category, runID, db_location):
  unit.driver.get(url)
  time.sleep(10)
  unit.read_results(db_location, runID, search_category)
# Shuts down the browser once we are done with it.
def cleanup_browser(unit):
    unit.quit()

# Blank analysis
def load_results():
    pass

# Blank analysis
def test_stat(observed_values, unit_assignments):
    pass


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


def create_translation_db(database):
	sql_create_table = """CREATE TABLE IF NOT EXISTS profile_names (
                                        runID text NOT NULL,
                                        profile_ID text NOT NULL,
                                        profile_name text NOT NULL,
                                        checkin_date text NOT NULL,
                                        checkout_date text NOT NULL
                                        )"""
	conn = create_connection(database)
	# create tables
	if conn is not None:
		# create projects table
		create_table(conn, sql_create_table)
	else:
		print("Error! cannot create the database")

def create_translation_db_macy(database):
  sql_create_table = """CREATE TABLE IF NOT EXISTS profile_names_macy (
                                        runID text NOT NULL,
                                        profile_ID text NOT NULL,
                                        profile_name text NOT NULL
                                        )"""
  conn = create_connection(database)
  # create tables
  if conn is not None:
    # create projects table
    create_table(conn, sql_create_table)
  else:
    print("Error! cannot create the database")


def create_translation_db_macy_search(database):
  sql_create_table = """CREATE TABLE IF NOT EXISTS profile_names_search_macy (
                                        runID text NOT NULL,
                                        profile_ID text NOT NULL,
                                        profile_name text NOT NULL,
                                        search_category text NOT NULL
                                        )"""
  conn = create_connection(database)
  # create tables
  if conn is not None:
    # create projects table
    create_table(conn, sql_create_table)
  else:
    print("Error! cannot create the database")


# def insert_into_db_macys(database_name, runID, treatment_names):
#   to_add = [{'runID': runID, "profile_name": name, 'profile_ID': num} for num, name in enumerate(treatment_names)]

def insert_into_db_outer(database_name, to_add, table_name):
  print(to_add)
  db = sqlite3.connect(database_name)
  curr = db.cursor()
  try:
    columns = ', '.join(to_add[0].keys())
    placeholders = ':'+', :'.join(to_add[0].keys())
    query = 'INSERT INTO %s (%s) VALUES (%s)' % (table_name, columns, placeholders)
    print(query)
    curr.executemany(query, to_add)

  except Error as e:
    print("Couldn't add to the database")
    print(e)
  db.commit()
  db.close()


def run_macy_search_experiment(runID, db_location, category, url, all_treatment_names=['control', 'female', 'male', 'youth', 'senior', 'female_panagotis', 'male_panagotis', 'youth_panagotis', 'senior_panagotis']):
  dic_treatment = create_treatment_dict()
  log_file = "%s_%s.log" % (runID, category)
  all_treatments = [dic_treatment[x] for x in all_treatment_names]
  to_add = [{'runID': runID, "profile_name": name, 'profile_ID': num, 'search_category' : category} for num, name in enumerate(all_treatment_names)]
  create_translation_db_macy_search(db_location)

  insert_into_db_outer(db_location, to_add, "profile_names_search_macy")
  measurement_wrapper = lambda unit : measurement_macy_search(unit, url, category, runID, db_location)
  make_unit_wrapper = lambda unit_id, treatment_id, block_id : make_browser_macy_search(unit_id, treatment_id, log_file, block_id)
  adfisher.do_experiment(make_unit=make_unit_wrapper, treatments=all_treatments,
                          measurement=measurement_wrapper, end_unit=cleanup_browser,
                          load_results=load_results, test_stat=test_stat, ml_analysis=False,
                          num_blocks=1, num_units=len(all_treatments), timeout=40000,
                          log_file=log_file, exp_flag=True, analysis_flag=False,
                          treatment_names=all_treatment_names)


def run_macy_experiment(runID, db_location, fname, all_treatment_names=['control', 'female', 'male', 'youth', 'senior', 'female_panagotis', 'male_panagotis', 'youth_panagotis', 'senior_panagotis']):
  dic_treatment = create_treatment_dict()
  log_file = "%s_%s" % (runID, fname.split(".")[0])
  all_treatments = [dic_treatment[x] for x in all_treatment_names]
  to_add = [{'runID': runID, "profile_name": name, 'profile_ID': num} for num, name in enumerate(all_treatment_names)]
  create_translation_db_macy(db_location)

  insert_into_db_outer(db_location, to_add, "profile_names_macy")
  measurement_wrapper = lambda unit : measurement_macy(unit, fname, runID, db_location)
  make_unit_wrapper = lambda unit_id, treatment_id, block_id : make_browser_macy(unit_id, treatment_id, log_file, block_id)
  adfisher.do_experiment(make_unit=make_unit_wrapper, treatments=all_treatments,
                          measurement=measurement_wrapper, end_unit=cleanup_browser,
                          load_results=load_results, test_stat=test_stat, ml_analysis=False,
                          num_blocks=1, num_units=len(all_treatments), timeout=40000,
                          log_file=log_file, exp_flag=True, analysis_flag=False,
                          treatment_names=all_treatment_names)


def run_experiment(city, checkin_date, checkout_date, runID, db_location):
  dic_treatment = create_treatment_dict()
  log_file = "%s_%s_%s_%s" % (runID, city, checkin_date, checkout_date)
  all_treatment_names = ['control', 'female', 'male', 'youth', 'senior', 'female_panagotis', 'male_panagotis', 'youth_panagotis', 'senior_panagotis']
  all_treatments = [dic_treatment[x] for x in all_treatment_names]
  to_add = [{'runID': runID, "profile_name": name, 'profile_ID': num, 'checkin_date': checkin_date, 'checkout_date': checkout_date} for num, name in enumerate(all_treatment_names)]
  create_translation_db(db_location)
  insert_into_db_outer(db_location, to_add, 'profile_names')

  measurement_wrapper = lambda unit : measurement_recommended(unit, city, checkin_date, checkout_date, runID, db_location)
  make_unit_wrapper = lambda unit_id, treatment_id, block_id : make_browser(unit_id, treatment_id, log_file, block_id)
  adfisher.do_experiment(make_unit=make_unit_wrapper, treatments=all_treatments,
	                        measurement=measurement_wrapper, end_unit=cleanup_browser,
	                        load_results=load_results, test_stat=test_stat, ml_analysis=False,
	                        num_blocks=1, num_units=len(all_treatments), timeout=40000,
	                        log_file=log_file, exp_flag=True, analysis_flag=False,
	                        treatment_names=all_treatment_names)
