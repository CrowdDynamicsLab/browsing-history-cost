
from datetime import date
import datetime
from dateutil.relativedelta import relativedelta
import pandas as pd
import sys

import kayak_hotel_wrapper
import argparse
import random


today = date.today()
print("Today is %s" % str(today))
seed = today.year + today.month + today.day
random.seed(seed)


if __name__ == '__main__':
	parser = argparse.ArgumentParser(description='Handle run.')
	parser.add_argument('-cities_file', type=str, help='pair_file', default = None)
	parser.add_argument('-city', type = str, help = 'direct input city', default = None, nargs = "+")
	parser.add_argument('-checkin_date', type=str, help='checkin date', default = None)
	parser.add_argument('-checkout_date', type=str, help='checkout date', default= None)
	parser.add_argument('runID', type = str, help = 'runID for organization')
	parser.add_argument("db_location", type = str, help = "db name")
	args = parser.parse_args()

	if args.checkin_date is  None:
		checkin_date = date.today() + relativedelta(months=+2)
	else:
		checkin_date = args.checkin_date
	if args.checkout_date is None:
		checkout_date = checkin_date + relativedelta(days=+1)
	else:
		checkout_date = args.checkout_date

	if args.cities_file is not None:
		city = pd.read_csv(args.cities_file, header = None)
		print(city)
		city = city[0].values.tolist()
	elif args.city is not None:
		city = args.city
	else:
		sys.exit("Either city file or city should be not None")

	random.shuffle(city)
	id_part = datetime.datetime.now().strftime("%Y-%m-%d_%H:%M")
	runID = "%s_%s" % (args.runID, id_part)
	for elem in city:
		kayak_hotel_wrapper.run_experiment(elem, str(checkin_date), str(checkout_date), runID, args.db_location)
