'''
Class to build data of yearly averages for a given month.
Items for use in class instances are:
- frame: A pandas DataFrame of the averages with columns "year" and "avg"
- year_list: A list of the years processed
- avg_list: A list of the averages processed
'''
import utils.mongodb as db
from collections import defaultdict
import pandas as pd
import numpy as np

class WeatherException(Exception):
    pass


class Averages:
    '''Set up the database connection
    and the year and averages lists.
    '''
    def __init__(self):
        try:
            self.db_conn = db.WeatherDb()
        except db.MongoDBException as e:
            raise WeatherException(e.__str__())

        # frame will be set to pandas DataFrame later
        self.frame = None
        self.year_list = []
        self.avg_list = []


    def set_values(self, station_id, month, start_year, end_year):
        '''Make sure the collection exist before trying to set.'''
        try:
            self.db_conn.check_for_collection(station_id)
        except db.MongoDBException as e:
            raise WeatherException(e.__str__())


        self.db_conn.set_collection(station_id)
        self.month = month

        # if years not provided, get from the database
        if start_year == None:
            self.start_year = self.db_conn.get_min_date()
            self.start_year = self.start_year.split('-')[0]
        else:
            self.start_year = start_year

        if end_year == None:
            self.end_year = self.db_conn.get_max_date()
            self.end_year = self.end_year.split('-')[0]
        else:
            self.end_year = end_year


    def _get_average(self, d):
        '''build the averages using the defaultdict.
        Expects each key to have 2 2-item tuples.
        If both tuples are not present, the date is skipped for averaging.'''
        tmin = []
        tmax = []
        for k in d.keys():
            entries = d[k]
            # if either is missing skip
            if len(entries) < 2:
                continue

            if entries[0][0] == 'tmin':
                tmin.append(entries[0][1])
                tmax.append(entries[1][1])
            else:
                # entries[0][0] must be tmax
                tmax.append(entries[0][1])
                tmin.append(entries[1][1])

                # both should be the same length.
        return ((sum(tmin) / len(tmin)) + (sum(tmax) / len(tmax))) / 2


    def _build_dict(self, records):
        '''builds our defaultdict of date keys and
        list value of 2 2-tuples'''
        mydict = defaultdict(list)
        for rec in records:
            day = rec.get('date').split('T')[0]
            if rec.get('datatype') == 'TMAX':
                dt = 'tmax'
            else:
                dt = 'tmin'
            temp = rec.get('value')
            mydict[day].append((dt, temp))
        return mydict


    def build_averages(self):
        '''Loops thru the years getting records for the month suppled.
        Ends up with pandas DataFrame self.frame, and two lists:
        self.year_list and self.avg_list'''
        avgdict = dict()
        for yr in range(int(self.start_year), int(self.end_year) + 1):
            #print('Checking {}-{:02d}'.format(yr, int(self.month)))
            records = self.db_conn.get_records('{}-{}'.format(yr, self.month.zfill(2)))
            if records == None:
                print('No data for {}-{}... skipping.'.format(yr, self.month.zfill(2)))
                continue
            mydict = self._build_dict(records)
            avg_temp = self._get_average(mydict)
            avgdict[yr] = avg_temp

        for k in sorted(avgdict.keys()):
            self.year_list.append(k)
            self.avg_list.append(avgdict.get(k))

        self.frame = pd.DataFrame({
            'year': self.year_list,
            'avg': self.avg_list})

        self.polyvalue = np.poly1d(np.polyfit(self.year_list, self.avg_list, 1))(self.year_list)
        self.rollingvalue = round(len(self.year_list) / 10)
        return



    def show_stations(self):
        '''Print station information for available collections'''
        self.db_conn.list_collections()
