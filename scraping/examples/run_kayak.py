
from datetime import date
import datetime
from dateutil.relativedelta import relativedelta
import pandas as pd
import sys

import kayak_wrapper
import argparse
import random


today = date.today()
print("Today is %s" % str(today))
seed = today.year + today.month + today.day 
random.seed(seed)


if __name__ == '__main__':
	parser = argparse.ArgumentParser(description='Handle run.')
	parser.add_argument('-flight_pair_file', type=str, help='pair_file', default = None)
	parser.add_argument('-flight_pair', type = str, help = 'direct input flight pair', default = None, nargs = "+")
	parser.add_argument('-depart_date', type=str, help='depart_date', default = None)
	parser.add_argument('-return_date', type=str, help='return date', default= None)
	parser.add_argument('runID', type = str, help = 'runID for organization')
	parser.add_argument("db_location", type = str, help = "db name")
	args = parser.parse_args()
	
	if args.depart_date is  None:
		depart_date = date.today() + relativedelta(months=+2)
	else:
		depart_date = datetime.datetime(args.depart_date, "%Y-%m-%d")
	if args.return_date is None:
		return_date = depart_date + relativedelta(weeks=+1)
	else:
		return_date = datetime.datetime(args.return_date, "%Y-%m-%d")

	if args.flight_pair_file is not None:
		flight_pair = pd.read_csv(args.flight_pair_file, header = None)
		print(flight_pair)
		flight_pair = flight_pair[0].values.tolist()
	elif args.flight_pair is not None:
		flight_pair = args.flight_pair
	else:
		sys.exit("Either flight pair file or flight pair should be not None")

	random.shuffle(flight_pair)
	id_part = datetime.datetime.now().strftime("%Y-%m-%d_%H:%M")
	runID = "%s_%s" % (args.runID, id_part) 
	for elem in flight_pair:
		kayak_wrapper.run_experiment(elem, str(depart_date), str(return_date), runID, args.db_location)
