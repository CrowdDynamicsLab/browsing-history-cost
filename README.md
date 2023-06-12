### Basic info
This repo is split into 2 parts

## modeling

#There are two notebooks for implementing hotels and flights respectively 

We present 2 data files to run into the model for flights
model_input_paper.csv - Used for running the binomial model
model_input_dollar_paper.csv - Used for running the price diff model

And 1 data file for hotels
compare_table_full.csv

## scraping

scrapping is mostly based off of AdFisher (see https://fairlyaccountable.org/adfisher/)
note that this was run on python 3.65 on a Linux box. (Red Hat Enterprise Linux Server release 7.9 (Maipo))

For the site_files the respective authors provided them - reach out to them for access
(https://nms.kcl.ac.uk/netsys/datasets/partisan-tracking/)
(https://ojs.aaai.org/index.php/ICWSM/article/view/7276)



### Installation. 

pip install -r requirements.txt should cover it

For scraping you will also need to install geckodriver
https://stackoverflow.com/questions/40208051/selenium-using-python-geckodriver-executable-needs-to-be-in-path