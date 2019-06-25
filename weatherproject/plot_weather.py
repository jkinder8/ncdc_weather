'''
plot_weather.py
Main method for interfacing with the weather.Averages class.
Enter "python plot_weather.py -v" for usage with examples.

Output: A plot of the station(s) and year(s) for a month.
'''

import matplotlib.pyplot as plt
import  utils.weather as weather

def show_usage():
    print('plot_weather.py usage'.center(80,'*'))
    print('Description: Plots average tempurature data for given weather station(s) for given month and years.\n')
    print('{:21s}=> Required: The station id for the request.'.format('station_id(s)'))
    print('\t\t\tYou can provide up to three stations, comma delimited with no spaces.')
    print('{:21s}=> Required: The month to average.'.format('month'))
    print('{:21s}=> Optional: The start year for the request. Format = yyyy'.format('[-s|--start]'))
    print('{:21s}=> Optional: The end year for the request. Format = yyyy'.format('[-e|--end]'))
    print('\n{:21s}=> If provided, list collections in mongo and exits. No other options needed.'.format('[-l|--list]'))
    print('\nIf no start or end dates it will look for the minimum and maximum years in mongo.')
    print('It isn\'t required but if using more than one station,you should use dates.')
    print('\nExamples:\n# Plot all January data for a single station.')
    print('\tpython ./plot_weather.py -i STATIONID -m 1')
    print('Plot all January data for three stations between 1970 and 1990.')
    print('\tpython ./plot_weather.py -i STATIONID_1,STATIONID_2,STATIONID_3 -m 1 -s 1970 -e 1990')
    print('\nIf plotting a single station, you get plots for monthly average, straight-line reqression,')
    print('and a moving average. If for more than one station, you only get the monthly averages.')
    print('*' * 80)
    exit(1)



def give_hint_and_exit():
    '''One of the options is missing or incorrect. Show how to get
    detailed usage.'''
    print('Enter python get_weather.py -v for detailed usage and examples')
    exit(1)


def list_stations():
    '''For -l option. Will show collections in mongo and exit.'''
    try:
        wa = weather.Averages()
        wa.show_stations()
    except weather.WeatherException as e:
        print(e.__str__())

    exit(0)

if __name__ == '__main__':
    '''
    Sets up the ArgumentParser and validates.
    The station id's provided will be placed in station_list[].
    After all the house keeping, the main loop iterates through
    the station_list, saving the id to variable station_id and then
    using the index of that list element to create an instance of the
    weather.Averages class and puts the plots together based on the
    class instance DataFrame.
    '''
    from argparse import ArgumentParser

    station_list = [] # list to hold the stations
    # Dict to convert month number for plot title
    month_names = {1: 'January', 2: 'February', 3: 'March', 4: 'April', 5: 'May', 6: 'June',
                   7: 'July', 8: 'August', 9: 'September', 10: 'October', 11: 'November', 12: 'December'}

    parser = ArgumentParser()
    parser.add_argument('-i', '--id',
                        help='Required. The station_id to use. Can be up to three separated by comma, no spaces.')
    parser.add_argument('-m', '--month', help='Month of year (01-12) to average.')
    parser.add_argument('-s', '--start', help='Optional. The start year (yyyy). Will pull lowest from the database if not provided.')
    parser.add_argument('-e', '--end',
                        help='Optional. The end year (yyyy). Will pull highest from the database if not provided.')
    parser.add_argument('-l', '--list', action='store_true', help='Prints list of collections and exits.')
    parser.add_argument('-v', '--verbose', action='store_true', help='Show detailed usage.')
    args = parser.parse_args()

    # -v... show usage with examples and exit
    if args.verbose:
        show_usage()

    # -l was given. Show the collections in mongo then exit
    if args.list:
        list_stations()

    # I put a limit of 5... it is just arbitrary
    # remove it if you want more
    if args.id.count(',') > 5:
        print('Maximum number of stations is 5.')
        give_hint_and_exit()

    # append all stations to station_list
    for sid in args.id.split(','):
        station_list.append(sid)

    # make sure month can be converted to int
    try:
        int(args.month)
    except ValueError:
        print('Month is not an integer value.')
        give_hint_and_exit()

    month = args.month

    # check year formats
    start_year = None
    if args.start:
        try:
            start_year = int(args.start)
        except TypeError:
            print('Start year must be 4 integers: yyyy')
            exit(1)

    end_year = None
    if args.end:
        try:
            end_year = int(args.end)
        except TypeError:
            print('End year must be 4 integers: yyyy')
            exit(1)


    try:
        for idx in range(len(station_list)):
            # get the station_id before a class object eats it!
            station_id = station_list[idx]
            station_list[idx] = weather.Averages()

            station_list[idx].set_values(station_id, month, start_year, end_year)

            print('Station id: {}\tMonth: {}'.format(station_id, month))
            ret = station_list[idx].build_averages()
            plt.plot(station_list[idx].frame[['year']], station_list[idx].frame[['avg']], label=station_id)

        # if it were only 1, print the regression and ma lines
        if len(station_list) == 1:
            plt.plot(station_list[0].year_list, station_list[0].polyvalue,
                     linestyle='-', color='r', label='SL Regression')
            plt.plot(station_list[0].frame[['year']], station_list[0].frame[['avg']].rolling(station_list[0].rollingvalue).mean(center=True),
                 linestyle='-', color='g', label='Moving Avg')

        plt.title('{} Averages'.format(month_names.get(int(month))))
        plt.xlabel('Year')
        plt.ylabel('Temp')
        plt.grid()
        plt.legend()
        plt.show()

    except weather.WeatherException as e:
        print(e.__str__())
        exit(1)

    exit(0)