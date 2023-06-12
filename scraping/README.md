## AdFisher

## See the base code (https://github.com/tadatitam/info-flow-experiments) for more functionality and potential other debugging for getting started

# For our purposes we have the following for flights
AdFisher/core/kayak.py - main unit that handles the actual collection
AdFisher/example/kayak_wrapper.py - handles setting up the treatments and controls and how to process them
AdFisher/example/run_kayak.py - Entry to run 

# And the following for hotels and macy
AdFisher/core/kayak_hotels.py - main unit that handles the actual collection
AdFisher/example/kayak_hotel_wrapper.py - handles setting up the treatments and controls and how to process them
AdFisher/example/run_kayak_hotel.py - Entry to run 

# All list of websites should be placed in the site_files folder

AdFisher/example/site_files/popular.txt - Example of how to format website list 


To retrive the site files for Agarwal et all follow:
https://nms.kcl.ac.uk/netsys/datasets/partisan-tracking/

To retrieve the profiles for Aspuld et al please contact the authors

# To make changes to what you want to make treated you need to update the kayak_wrapper to 
# add treatments that you want to run

To run this you can run python run_kayak.py. The arguments are given below
runID: Tag to help distinguish between runs
db_location - a sqllite db to store the data
--depart_date - specific date to depart (default to 2month)
--return_date - specific date to return (default to depart_date + 1w)
--flight_pair_file - a textfile with the flight pairs to look. see for example 'example.csv'
--flight_pair - can directly specify a flight pair to run, ex "JFK-LAX"


pip install -r requirements.txt  should get all relevant dependencies 
geckodriver will also be needed as a part of selenium 

