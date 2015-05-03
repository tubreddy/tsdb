# tsdb
## Telangana Habitat  Details
This is a Python script to written to extract the all habitat details of Telangana state in India.
Typically Indian states have majorly four layers of habitat division for administration purpose.
Namely.
* State
* District
* Mandal
* Grampanchayt
* Village.

This script extrcats the data by each district(minus Hyderabad) down to grampanchayat level and captures all habitations in a singledatabase.People can you use this for multiple places as per their coneveninece.

## #How to use this script

1.First, if you want to directly use the Telangana Habitat database for any of your needs just download databse file - telanganadb_salchemy.db and open it in your sqllite browser.
2.If you want to run thepython scripcts to generate databse you can do the following.
*    a. Create your own python virtual environment
*    b. pip install < requirements.txt
*    c. run python tsdb_tables.py  Comment: to create tables
*    d. run python tsdb_habitats.py comment: to create database
*    e. Create an account with plotly
*    d. run python tshabitatplot.py
