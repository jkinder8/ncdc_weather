This application uses data from https://www.ncdc.noaa.gov

To use it, you must first request a token. See Step 1 on the following page.
https://www.ncdc.noaa.gov/cdo-web/webservices/v2

At last count there were over 105,000 stations listed. Some stations have data
going back to the early 1900's while others have been recently added.

Requires a local mongo database.
The json needed to create the stations collection is included.
Import:
mongoimport -d weather -c stations --type json weather_db_stations.json

Also there is json here for Nome, Alaska for the month of January from
1910 to 2018: nome.json
mongoimport -d weather -c USW00026617 --type json nome_ak_Jan.json

get_weather.py and plot_weather.py have verbose help with examples (-v option)

* Prior to using get_weather.py, either place the token you received in the default
for parser.add_argument default value or remove the default entirely if you wish
to provide each time. 

Python version used: 3.7.0

Python installs used:
- pymongo
- numpy
- pandas
- requests