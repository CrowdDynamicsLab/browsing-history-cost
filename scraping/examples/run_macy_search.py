from datetime import date
import datetime
from dateutil.relativedelta import relativedelta
import sys

import kayak_hotel_wrapper
import argparse
import random

today = date.today()
print("Today is %s" % str(today))
seed = today.year + today.month + today.day
random.seed(seed)
import pandas as pd

import pdb
if __name__ == '__main__':
  parser = argparse.ArgumentParser(description='Handle run.')
  parser.add_argument('-search_file', type=str, help='csv of categories,urls', required=True)
  parser.add_argument('-profiles_to_use', help='which profiles_to_use', default=None, nargs="+", type=str)
  parser.add_argument('runID', type=str, help='runID for organization')
  parser.add_argument("db_location", type=str, help="db name")
  args = parser.parse_args()
  print(args.profiles_to_use)

  search = pd.read_csv(args.search_file)

  id_part = datetime.datetime.now().strftime("%Y-%m-%d_%H:%M")
  runID = "%s_%s" % (args.runID, id_part)
  for index, row in search.iterrows():
      if args.profiles_to_use is not None:
        kayak_hotel_wrapper.run_macy_search_experiment(runID, args.db_location, row['category'], row['url'], args.profiles_to_use)
      else:
        kayak_hotel_wrapper.run_macy_search_experiment(runID, args.db_location, row['category'], row['url'])
