'''''
Main interface to the weather utilities
Enter "python get_weather.py -v" for details on usage with examples.
'''
from utils.date_util import Dates
from utils.ncdc import NcdcWeather
import utils.mongodb as db
import json

def show_usage():
    '''Long-winded / detailed usage'''
    print('get_weather.py usage'.center(80,'*'))
    print('Description: Gets MIN / MAX tempurature data for a given weather station.\n')
    print('{:21s}=> Required: The station id for the request.'.format('[-i|--id]'))
    print('{:21s}=> Required: The start date for the request. Format = yyyy[-mm-dd]'.format('[-s|--start]'))
    print('\t\t\tIf the format is yyyy, it is set to the beginning of the year')
    print('\t\t\tand loops through the entire year.')
    print('\t\t\tIf the format is yyyy-mm, -dd is set to first of the month.')
    print('\t\t\tIf the format is yyyy-mm and no end date, will loop through the entire month.')
    print('\t\t\tIf it is the text "minmax", gets the min and max dates from mongo.')
    print('{:21s}=> Optional. If the end date is not given, will just get for start date.'.format('[-e|--end]'))
    print('\t\t\tFormat = yyyy-mm[-dd].')
    print('\t\t\tIf format is yyyy-mm, -dd is set to the end of the month.')
    print('\t\t\t*** yyyy must be the same for start and end dates.')
    print('{:21s}=> Required if not [-d|--database]. The ncdc token to use.'.format('[-t|--token]'))
    print('{:21s}=> Optional. If supplied will make the request to local mongodb.'.format('[-d|--database]'))
    print('\t\t\tOtherwise it will pull from the ncdc weather site.')
    print('{:21s}=> Optional. Only used if you want ncdc data to go to stdout instead of'.format('[-o|--stdout]'))
    print('\t\t\tinserting in the database. Automatically set if [-d|--database].')
    print('\n{:21s}=> If provided, list collections in mongo and exits. No other options needed.'.format('[-l|--list]'))
    print('\n\t\t\t**NOTE: All requests are broken down to a maximum of 7 days per db or ncdc call.')
    print('\t\t\tIt will loop through 7 days at a time until the requested days are exhausted.')
    print('\nExamples:\n# Get a single day from ncdc and add to mongodb.')
    print('\tpython ./get_weather.py -i STATIONID -s 2016-02-10 -t MYTOKEN')
    print('\n# Get date range from ncdc and print to stdout.')
    print('\tpython ./get_weather.py -i STATIONID -s 2016-02-10 -e 2016-02-17 -t MYTOKEN -o')
    print('\n# Get the entire month of February 2016 (leap year) from ncdc and insert in mongo.')
    print('\tpython ./get_weather.py -i STATIONID -s 2016-02 -t MYTOKEN')
    print('\n# Get all of February and March of 2016 (leap year) from mongodb... stdout by default.')
    print('\tpython ./get_weather.py -d -i STATIONID -s 2016-02 -e 2016-03')
    print('\n# Get minimum and maximum dates from mongodb and exit... stdout by default.')
    print('\tpython ./get_weather.py -i STATIONID -s minmax')
    print('\n# List current collections in mongo and exit... stdout by default.')
    print('\tpython ./get_weather.py -l')
    print('*' * 80)
    exit(0)



def check_date(day):
    '''Checks the data format: yyyy[-mm-dd] and that they can
    be converted to integers.'''
    date_list = day.split('-')
    for i in range (len(date_list)):
        if i == 0 and len(date_list[i]) != 4:
            print("Year needs to be 4 digits.")
            return False
        elif i > 0 and len(date_list[i]) != 2:
            print("Months and days need to be 2 digits")
            return False
        try:
            int(date_list[i])
        except ValueError:
            print('{} is not numeric.'.format(date_list[i]))
            return False
    return True



def give_hint_and_exit():
    '''One of the options is missing or incorrect. Show how to get
    detailed usage.'''
    print('Enter python get_weather.py -v for detailed usage and examples')
    exit(1)


def check_station_id(id):
    '''Checks that the station id provided is in the weather.stations collection.
    I added this since a call to ncdc with an invalid station just retuns an
    empty json, which could be confused for no data for the date range given.'''
    try:
        s = db.Stations()
        return True
    except db.MongoDBException as e:
        print(e.__str__())
        return False


def list_stations():
    '''For -l option. Will show collections in mongo and exit.'''
    from utils.weather import Averages
    try:
        s = Averages()
        s.show_stations()
    except Exception as e:
        print(e.__str__())

    exit(0)


def send_to_print(data):
    '''Print to stdout the dates and min / max values.'''
    for rec in data:
        if rec.get('datatype') == 'TMIN':
            print('{}: Min = {}'.format(rec.get('date').split('T')[0], rec.get('value')))
        if rec.get('datatype') == 'TMAX':
            print('{}: Max = {}'.format(rec.get('date').split('T')[0], rec.get('value')))


def get_min_and_max_dates(id):
    '''Show lowest and highest dates in mongo for the given station id'''
    try:
        d = db.WeatherDb()
        d.check_for_collection(id)
        d.set_collection(id)
        min = d.get_min_date()
        max = d.get_max_date()
        print('{} - Min: {}\tMax: {}'.format(id, min, max))
    except db.MongoDBException as e:
        print(e.__str__())

    exit(0)


if __name__ == '__main__':
    from argparse import ArgumentParser

    parser = ArgumentParser()
    parser.add_argument('-i', '--id', help='Required. The station_id to use.')
    parser.add_argument('-d','--database', action='store_true', help='If supplied, will use the mongodb instead of the ncdc site.')
    parser.add_argument('-s', '--start', help='Required. The start date for the query or "min". Use -v for more informtion.')
    parser.add_argument('-e', '--end', help='The end date for the query or "max". If not supplied it will be a request for a single day.')
    parser.add_argument('-t', '--token', help='The token for the ncdc site. Not needed if -d is set.',
                        default='PLACE_YOUR_TOKEN_HERE')
    parser.add_argument('-o', '--stdout', action='store_true', help='Will print to stdout if supplied. If -d is set, it will be automatically set to stdout')
    parser.add_argument('-l', '--list', action='store_true', help='Prints list of collections and exits.')
    parser.add_argument('-v', '--verbose', action='store_true', help='Show detailed usage.')
    args = parser.parse_args()

    # Show that huge help function then exit
    if args.verbose:
        show_usage()

    # -l was given. Show the collections in mongo then exit
    if args.list:
        list_stations()

    # id is required... check first.
    if args.id == None:
        print('> Station id is required.')
        give_hint_and_exit()

    # We need a token for ncdc if not a db request
    from_database = args.database
    to_stdout = args.stdout
    if not from_database:
        # not a db request... need ncdc token
        if args.token == None:
            print('> A token is required if not a database request.')
            give_hint_and_exit()
        token = args.token
    else:
        # args.stdout wasn't explicity set, but it is a db request
        # so setting to_stdout
        to_stdout = True

    if not args.start:
        print('> A start date is required.')
        give_hint_and_exit()

    # added to allow just retrieving the date range for the collection in mongo
    if args.start == 'minmax':
        get_min_and_max_dates(args.id)
    # not minmax so check
    elif not check_date(args.start):
        give_hint_and_exit()
    start_date = args.start
    if args.end == None:
        # end not provided... set to start
        end_date = start_date
    else:
        # check date format
        if not check_date(args.end):
            give_hint_and_exit()
        # must be good, set the variable
        end_date = args.end

    # Check that if both dates given year is the same
    if start_date.split('-')[0] != end_date.split('-')[0]:
        print('> Year must be the same for start and end dates.')
        give_hint_and_exit()

    # makes sure the station is in the stations collection.
    if not check_station_id(args.id):
        exit(1)

    # Get a yr variable to use for julian date manipulation
    yr = int(start_date.split('-')[0])
    d = Dates()
    # get julian date for dates.
    # if not yyyy-mm-dd, set to either 01-01 or mm-01
    j_start = d.get_julian_date(start_date, 0)
    j_end = d.get_julian_date(end_date, 1)

    data_conn = None
    db_conn = None
    if not from_database:
        # create ncdc instance
        data_conn = NcdcWeather(args.id, args.token)
    if from_database or not to_stdout:
        try:
            # db connection needed. Either to retrieve or insert data
            db_conn = db.WeatherDb()
            # If this request is for mongo, we don't want to create
            # an empty collection.
            if from_database:
                # Check that it is an existing collection given that
                # mongo will create it even without records.
                db_conn.check_for_collection(args.id)
            # set the collection to use from mongo.
            # if this is an ncdc request, will create the collection
            # if it doesn't already exist.
            db_conn.set_collection(args.id)
        except db.MongoDBException as e:
            print(e.__str__())
            exit(1)

    # Control the while loop with Julian dates
    current_j_day = j_start
    while current_j_day <= j_end:
        # we keep our request to a maximum of 7 days
        if j_end - current_j_day > 6:
            end_j_day = current_j_day + 6
        else:
            end_j_day = j_end

        # Get our current yyyy-mm-dd dates converted from the julian dates
        request_start_date = d.get_date(yr, current_j_day)
        request_end_date = d.get_date(yr, end_j_day)
        print('Processing dates: {} - {}'.format(request_start_date, request_end_date))
        if from_database:
            # for mongo I need to create a regex style pattern to send.
            # We have our first and last ones. Get the others to make
            # a pattern like 'yyyy-mm-dd|yyyy-mm-dd|...'
            count = current_j_day + 1
            pat = [request_start_date]
            while count < end_j_day:
                real_date = d.get_date(yr, count)
                pat.append(real_date)
                count += 1
            pat.append(request_end_date)
            return_data = db_conn.get_records('|'.join(x for x in pat))
            # Was a database request... goes to stdout
            if not return_data:
                print('No data.')
            else:
                send_to_print(return_data)

        else:
            # Request goes to the ncdc site
            return_data = data_conn.get_min_max_data(str(request_start_date), str(request_end_date))
            if not return_data:
                print('There was an issue getting the requested data.')
                exit(1)
            if to_stdout:
                results = json.loads(return_data)
                if not results.get('results'):
                    print('No data.')
                else:
                    send_to_print(results.get('results'))
            else:
                try:
                    db_conn.insert_json(return_data)
                except db.MongoDBException as e:
                    print(e.__str__())

        current_j_day = end_j_day + 1

    exit(0)

