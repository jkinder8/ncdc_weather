'''
Classes to be used with the local mongo database.
class WeatherDb:
    Is for the collections named after the ncdc station id's.
class Stations:
    Is for the collection named stations which has:
        station_id
        name
        lat
        lont
'''

import pymongo
import json
import re

class MongoDBException(Exception):
    pass



class WeatherDb:
    '''
    Class to work with the collections named for the station id's.

    '''
    def __init__(self):
        try:
            self.client = pymongo.MongoClient('localhost', 27017)
            self.db = self.client['weather']
            self.collection_set = False
        except:
            raise MongoDBException('Could not connect to the database.')



    def set_collection(self, id):
        self.collection = self.db[id]
        # index needed to keep dups from being inserted for date and datatype (min / max)
        if 'date_1_datatype_1' not in self.collection.index_information():
            self.collection.create_index([('date', pymongo.ASCENDING), ('datatype', pymongo.ASCENDING)],
                                         unique=True)

        # boolean used to check if we have a collection set
        # before making any calls in other methods
        self.collection_set = True


    def check_for_collection(self, id):
        if id not in self.db.list_collection_names():
            raise MongoDBException('Collection {} Not Found.'.format(id))



    def get_records(self, pat):
        '''Retrieves and returns data for the station id given
        the regex pattern sent.
        Checks if connected to a collection first.'''
        if self.collection_set == False:
            raise MongoDBException('Not connected to a collection.')

        results = self.collection.find({'date': re.compile(pat)})
        if results.count() == 0:
            return None
        return results



    def insert_json(self, rec):
        '''Attempts to insert the data rec provided in to the mongo collection.
        Checks if connected to a collection first.'''
        if self.collection_set == False:
            raise MongoDBException('Not connected to a collection.')

        try:
            json_rec = json.loads(rec)
            json_rec = json_rec['results']
            try:
                self.collection.insert(json_rec)
            except Exception as e:
                print('Exception received:', e.__str__())
            return True
        except ValueError as e:
            raise MongoDBException('JSON ValueError:', e.__str__())
        except KeyError:
            # if I get a key error, the results were empty
            raise MongoDBException('No records.')



    def get_min_date(self):
        '''will get the lowest date in mongo for this collection'''
        if self.collection_set == False:
            raise MongoDBException('Not connected to a collection.')

        result = self.collection.find().sort('date', 1).limit(1)
        try:
            return result.__getitem__(0).get('date').split('T')[0]
        except IndexError:
            raise MongoDBException('No data available for this collection.')


    def get_max_date(self):
        '''will get the highest date in mongo for this collection'''
        if self.collection_set == False:
            raise MongoDBException('Not connected to a collection.')

        result = self.collection.find().sort('date', -1).limit(1)
        try:
            return result.__getitem__(0).get('date').split('T')[0]
        except IndexError:
            raise MongoDBException('No data available for this collection.')


    def list_collections(self):
        '''Print station information for available collections'''
        try:
            s = Stations()
            id_list =  self.db.list_collection_names()
            print('\n{:20}{:30}{:15}{:15}'.format('Station ID', 'Station Name', 'Lat', 'Lon'))
            print('{:20}{:30}{:15}{:15}'.format('-' * 12, '-' * 25, '-' * 10, '-' * 10))
            for id in id_list:
                if id != 'stations':
                    station_info = s.get_station_name(id)
                    print('{:20}{:30}{:<15}{:<15}'.format(id, station_info.get('name'),
                                    station_info.get('lat'), station_info.get('lon')))
        except MongoDBException as e:
            print('Mongo Exception Caught:', e.__str__())




class Stations:
    '''Class for working with the stations collection.'''
    def __init__(self):
        try:
            self.client = pymongo.MongoClient('localhost', 27017, connect=True)
            self.db = self.client['weather']
            self.collection = self.db['stations']
        except:
            raise MongoDBException('Could not connect to the database.')


    def get_station(self, id):
        # validates that the station_id is valid from our local
        # stations collection
        return self.collection.find_one({"station_id" : id })


    def get_station_name(self, id):
        '''For print information about the station id provided'''
        return self.collection.find_one({'station_id': id},{'_id':0, 'name':1, 'lat': 1, 'lon': 1})


    def get_upper(self, coordinate, coordinate_range):
        '''return the upper search limit based on conditions.'''
        if coordinate_range == 0 and coordinate >= 0:
            return coordinate + 1
        elif coordinate_range == 0 and coordinate < 0:
            return coordinate
        elif coordinate < 0:
            return coordinate + coordinate_range - 1
        return coordinate + coordinate_range
    
    

    def get_lower(self, coordinate, coordinate_range):
        '''return the lower search limit based on conditions.'''
        if coordinate_range == 0 and coordinate >= 0:
            return coordinate
        elif coordinate_range == 0 and coordinate < 0:
            return coordinate - 1
        elif coordinate < 0:
            return coordinate - coordinate_range + 1
        return coordinate - coordinate_range



    def build_query(self, d):
        '''Builds the $and query based on the received dict.'''
        qstr = {'$and': []}
        val = d.get('lat_lower')
        if val != None:
            if val < 0:
                qstr.get('$and').append({'lat': {'$gt': val}})
            else:
                qstr.get('$and').append({'lat': {'$gte': val}})
            val = d.get('lat_upper')
            if val < 0:
                qstr.get('$and').append({'lat': {'$lte': val}})
            else:
                qstr.get('$and').append({'lat': {'$lt': val}})
        val = d.get('lon_lower')
        if val != None:
            if val < 0:
                qstr.get('$and').append({'lon': {'$gte': val}})
            else:
                qstr.get('$and').append({'lon': {'$gt': val}})
            val = d.get('lon_upper')
            if val < 0:
                qstr.get('$and').append({'lon': {'$lt': val}})
            else:
                qstr.get('$and').append({'lon': {'$lte': val}})
        return qstr



    def get_locations(self, lat, latpm, lon, lonpm):
        '''Check which args are not empty, set the ranges,
        build the monog request and get the results.'''
        qdict = {}
        if lat != '':
            lat_lower = self.get_lower(lat, latpm)
            qdict['lat_lower'] = lat_lower
            lat_upper = self.get_upper(lat, latpm)
            qdict['lat_upper'] = lat_upper
        if lon != '':
            lon_lower = self.get_lower(lon, lonpm)
            qdict['lon_lower'] = lon_lower
            lon_upper = self.get_upper(lon, lonpm)
            qdict['lon_upper'] = lon_upper

        qstr = self.build_query(qdict)
        results = self.collection.find(qstr, {'_id': 0})
        if results.count() == 0:
            return None
        return results
            
