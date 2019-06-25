'''
Pass:
    station id: A station identified as GHCND
    start and end dates: yyyy-mm-dd

Build the query_string to send to the ncdc site and return
results.
'''
import requests


class NcdcWeather:
    '''
    Create an instance of the class with the station id,
    ncdc token, and optional record limit.
    '''
    url = 'https://www.ncdc.noaa.gov/cdo-web/api/v2/data'

    def __init__(self, station, token, limit=14):
        self.station = station
        self.token = token
        self.limit = limit


    def get_min_max_data(self, start_day, end_day):
        '''Gets the query string built and calls the ncdc site'''
        query_string =  self.__build_min_max_querystring(start_day, end_day)
        try:
            headers = {'token': self.token}
            response = requests.get(query_string, headers=headers, timeout=15)

            if self._check_status_code(response.status_code) == False:
                return False

            return response.text
        except requests.exceptions.RequestException as e:
            print("Request failed: %s" % (e))
            return False


    def __build_min_max_querystring(self,start_day,end_day):
        '''Builds the querstring to send to ncdc site'''
        return self.url + '?datasetid=GHCND&stationid=GHCND:' + self.station \
            + '&startdate=' + start_day + '&enddate=' + end_day + \
            '&datatypeid=TMIN&datatypeid=TMAX&units=standard&limit=' + str(self.limit)



    def _check_status_code(self,code):
        '''I should only be getting 200's as good request
        and the except from requests should catch the bad stuff'''
        if code == 200:
            return True
        else:
            return False