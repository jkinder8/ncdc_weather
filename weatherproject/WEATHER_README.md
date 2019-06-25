The weather utility can be used on command line for interacting with
pandas DataFrames created.
Example:
* sourced to the venv
python
Python 3.7.0 (default, Jun 28 2018, 13:15:42) 
[GCC 7.2.0] :: Anaconda, Inc. on linux
Type "help", "copyright", "credits" or "license" for more information.
>>> import utils.weather as w
>>> w1 = w.Averages()
>>> # I can see the available stations
... w1.show_stations()

Station ID          Station Name                  Lat            Lon            
------------        -------------------------     ----------     ----------     
USW00013874         ATLANTA HARTSFIELD INTL AP    33.63          -84.441        
GB000004500         LIBREVILLE                    0.38           9.45           
USW00026617         NOME MUNI AP                  64.511         -165.44        
COM00080370         SAN LUIS                      0.862          -77.672        
>>> # for w1, using USW00013874
... w1.set_values('USW00013874', '01', 1970, 1980)
>>> # tell it to build the averages
... w1.build_averages()
>>> # well alrighty... get another
... w2 = w.Averages()
>>> # Will use the same date range on all
... w2.set_values('USW00026617', '01', 1970, 1980)
>>> w2.build_averages()
>>> # How about a third
... w3 = w.Averages()
>>> w3.set_values('GB000004500', '01', 1970, 1980)
>>> w3.build_averages()
>>> # Create a combined DataFrame of all 3
... newdf = w1.frame
>>> # all have the col name 'avg'. I will add 2 and 3 with the station id
... newdf['USW00026617'] = w2.frame[['avg']].values
>>> newdf['GB000004500'] = w3.frame[['avg']].values
>>> # poor w1 would like a column name change also
... newdf.rename(columns={'avg': 'USW00013874'}, inplace=True)
>>> # Check the new combined dataframe
... newdf
    year  USW00013874  USW00026617  GB000004500
0   1970    35.919355    -4.241935    79.758065
1   1971    42.887097    -5.709677    79.516129
2   1972    46.741935     3.000000    79.806452
3   1973    41.354839    -5.274194    80.596774
4   1974    53.241935     5.080645    79.129032
5   1975    47.129032    -0.709677    79.758065
6   1976    38.483871     0.000000    79.225806
7   1977    29.290323    24.209677    79.387097
8   1978    33.629032    21.564516    80.903226
9   1979    37.258065    20.016129    80.935484
10  1980    44.870968     0.838710    80.983871
>>>