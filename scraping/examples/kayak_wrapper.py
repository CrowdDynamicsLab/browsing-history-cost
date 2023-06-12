import sys, os
sys.path.append("../core")          # files from the core
import adfisher                     # adfisher wrapper function
import web.pre_experiment.alexa     # collecting top sites from alexa
import web.kayak               # collecting ads
import argparse
import time

import sqlite3
from sqlite3 import Error



# Defines the browser that will be used as a "unit" and gives it a copy of the adblock_rules
def make_browser(unit_id, treatment_id, log_file, block_id = None):
    b = web.kayak.KayakUnit(log_file=log_file, unit_id=unit_id,
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


def exp_wrapper2(unit, name):
    unit.visit_sites(name)

# Measurement - Collects ads
# checks all the sites that adfisher could previously collect on
# (~10 minutes for src and href)
def measurement(unit, flight_pair, depart_date, return_date, runID, db_location):
    search = "https://www.kayak.com/flights/%s/%s/%s" % (flight_pair, depart_date, return_date)
    unit.driver.get(search)
    time.sleep(30)
    print("working on flight pair %s" % flight_pair)
    unit.read_results(db_location, runID, flight_pair, depart_date, return_date)

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
                                        depart_date text NOT NULL,
                                        return_date text NOT NULL
                                        )"""
    conn = create_connection(database)
    # create tables
    if conn is not None:
        # create projects table
        create_table(conn, sql_create_table)
    else:
        print("Error! cannot create the database")


def insert_into_db(database_name, runID, depart_date, return_date, treatment_names):
    create_translation_db(database_name)
    to_add = [{'runID' : runID, "profile_name" : name, 'profile_ID' : num, 'depart_date' : depart_date, 'return_date' : return_date} for num, name in enumerate(treatment_names)]
    print(to_add)
    db = sqlite3.connect(database_name)
    curr = db.cursor()
    try:
        columns = ', '.join(to_add[0].keys())
        placeholders = ':'+', :'.join(to_add[0].keys())
        query = 'INSERT INTO profile_names (%s) VALUES (%s)' % (columns, placeholders)
        print(query)
        curr.executemany(query, to_add)

    except Error as e:
        print("Couldn't add to the database")
        print(e)
    db.commit()
    db.close()


def run_experiment(flight_pair, depart_date, return_date, runID, db_location):
    treatments_names = ['female', 'male', '18-34', 'over65',  'women_panogotis',  'men_panogotis', 'youth_panogotis', 'senior_panogotis', '55-64', 'african_american', 'asian', 'caucasian', 'hispanic']
    female_treatment = lambda unit: exp_treatment_wrapper(unit, treatments_names[0])
    male_treatment = lambda unit: exp_treatment_wrapper(unit, treatments_names[1])
    youth_treatment = lambda unit: exp_treatment_wrapper(unit, treatments_names[2])
    senior_treatment = lambda unit: exp_treatment_wrapper(unit, treatments_names[3])
    female2_treatment = lambda unit: exp_treatment_wrapper(unit, treatments_names[4])
    male2_treatment = lambda unit: exp_treatment_wrapper(unit, treatments_names[5])
    youth2_treatment = lambda unit: exp_treatment_wrapper(unit, treatments_names[6])
    senior2_treatment = lambda unit: exp_treatment_wrapper(unit, treatments_names[7])
    middle_age_treatment = lambda unit: exp_treatment_wrapper(unit, treatments_names[8])
    african_american_treatment = lambda unit: exp_treatment_wrapper(unit, treatments_names[9])
    asian_treatment = lambda unit: exp_treatment_wrapper(unit, treatments_names[10])
    caucasian_treatment = lambda unit: exp_treatment_wrapper(unit, treatments_names[11])
    hispanic_treatment = lambda unit: exp_treatment_wrapper(unit, treatments_names[12])

    log_file = "%s_%s_%s_%s" % (runID, flight_pair, depart_date, return_date)

    # all_treatments = [control_treatment, female_treatment, male_treatment, youth_treatment, middle_age_treatment, senior_treatment,
    # 	african_american_treatment, asian_treatment, caucasian_treatment, hispanic_treatment]
    # all_treatments = [control_treatment, female_treatment, male_treatment, youth_treatment, senior_treatment, female2_treatment, male2_treatment, youth2_treatment, senior2_treatment]
    #all_treatments = [control_treatment, female_treatment, male_treatment, youth_treatment, senior_treatment, african_american_treatment, asian_treatment, caucasian_treatment, hispanic_treatment]

    # all_treatments = [control_treatment, female_treatment, male_treatment, youth_treatment, senior_treatment, female2_treatment, male2_treatment, youth2_treatment, senior2_treatment, middle_age_treatment, african_american_treatment, asian_treatment, caucasian_treatment, hispanic_treatment]
    all_treatments = [african_american_treatment, asian_treatment, caucasian_treatment, hispanic_treatment]
    #TODO SEND SURE the treatment names match the actual treatments
    all_treatment_names = ['african_american', 'asian', 'caucasian', 'hispanic']
    #all_treatment_names = ['control', 'female', 'male', 'senior', 'youth', 'female_patagon', 'male_patagon', 'senior_patagon' , 'youth_patagon']
    #all_treatments = [control_treatment]
    #all_treatment_names = ['control']
    #all_treatment_names = ['african_american', 'asian', 'caucasian', 'hispanic']
    #all_treatment_names = ['control', 'female', 'male', 'youth', 'senior', 'african_american', 'asian', 'caucasian', 'hisp
    #all_treatment_names = ['control'] + treatments_names
    insert_into_db(db_location, runID, depart_date, return_date, all_treatment_names)

    measurement_wrapper = lambda unit : measurement(unit, flight_pair, depart_date, return_date, runID, db_location)
    make_unit_wrapper = lambda unit_id, treatment_id, block_id : make_browser(unit_id, treatment_id, log_file, block_id)
    adfisher.do_experiment(make_unit=make_unit_wrapper, treatments=all_treatments,
                            measurement=measurement_wrapper, end_unit=cleanup_browser,
                            load_results=load_results, test_stat=test_stat, ml_analysis=False,
                            num_blocks=1, num_units=len(all_treatments), timeout=4000,
                            log_file=log_file, exp_flag=True, analysis_flag=False,
                            treatment_names=all_treatment_names)


def run_experiment_target(flight_pair, depart_date, return_date, runID, db_location, filenames, filetags):
    all_treatments = []
    log_file = "%s.log" % runID
    for fname in filenames:
        funct2 = lambda unit : exp_wrapper2(unit, fname)
        all_treatments.append(funct2)
    insert_into_db(db_location, runID, depart_date, return_date, filetags)
    measurement_wrapper = lambda unit : measurement(unit, flight_pair, depart_date, return_date, runID, db_location)
    make_unit_wrapper = lambda unit_id, treatment_id, block_id : make_browser(unit_id, treatment_id, log_file, block_id)
    adfisher.do_experiment(make_unit=make_unit_wrapper, treatments=all_treatments,
                            measurement=measurement_wrapper, end_unit=cleanup_browser,
                            load_results=load_results, test_stat=test_stat, ml_analysis=False,
                            num_blocks=1, num_units=len(all_treatments), timeout=4000,
                            log_file=log_file, exp_flag=True, analysis_flag=False,
                            treatment_names=filetags)
