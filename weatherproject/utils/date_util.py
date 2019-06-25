'''
A simple utility package for date manipulation.
Mostly for converting back and forth between
a yyyy-mm-dd formatted date and a julian date.
'''
import datetime
import calendar

class Dates:

    fmt = '%Y-%m-%d'

    def get_date(self, y, doy):
        """Return %Y-%m-%d formatted string given a year and julian date."""
        date = datetime.datetime(y,1,1) + datetime.timedelta(doy - 1)
        return date.strftime(self.fmt)

    def __convert__(self, s):
        '''convert string to struct_time'''
        dt = datetime.datetime.strptime(s, self.fmt)
        return dt.timetuple().tm_yday

    def __get_last_day_of_month__(self, y, m):
        """Returns the last day of the given year and month."""
        full_date = y + "-" + m + "-01"
        full_date = datetime.datetime.strptime(full_date, self.fmt)
        _, days_in_month = calendar.monthrange(full_date.year, full_date.month)
        return days_in_month

    def get_julian_date(self, dt, val=0):
        """Returns the julian date.
            dt = yyyy, yyyy-mm, yyyy-mm-dd
            if dt = yyyy-mm-dd it is converted.
            if dt = yyyy or yyyy-mm, val is determined
            if val = 0, set as either first day of given month or year
            if val = 1, set as either last day of given month or year
        """
        if dt.count('-') < 1:
            if val == 0:
                dt = dt + '-01-01'
            else:
                dt = dt + '-12-31'
        elif dt.count('-') < 2:
            if val == 0:
                dt = dt + "-01"
            else:
                ym = dt.split('-')
                last_day = self.__get_last_day_of_month__(ym[0], ym[1])
                dt = ym[0] + '-' + ym[1] + '-' + str(last_day)

        j = self.__convert__(dt)
        return j


