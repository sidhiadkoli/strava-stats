import calendar
from datetime import datetime
import logging
import re

from authenticate import Auth
from strava import Strava


class Stats:
    """Get requested statistics of the user's activities."""
    def __init__(self):
        self.auth = Auth()

    def parse_query(self, query_str):
        """Parse the requested query."""
        # TODO: Do something better than string matching.

        params = {}

        # Max filter.
        ma = re.match(r'([0-9]* ?)(longest|fastest|max elevation)', query_str)
        if ma:
            if ma.group(1):
                params['count'] = int(ma.group(1).strip())
            else:
                params['count'] = 1
            attr = ma.group(2)
            if attr == 'longest':
                params['filter_attr'] = 'distance'
            elif attr == 'fastest':
                params['filter_attr'] = 'speed'
            else:
                params['filter_attr'] = 'elevation'

        # Distance filter.
        ma = re.search(r'(([0-9]+)k)|(century)', query_str)
        if ma:
            if ma.group(0) == 'century':
                dist = 100
            else:
                dist = int(ma.group(2))
            params['distance'] = dist * 1000

        # Get time frame.
        # Note: the below regex matches a typo: sepember.
        ma = re.search(r'(jan(?:uary)?|feb(?:ruary)?|mar(?:ch)?|apr(?:il)?|may|jun(?:e)?|jul(?:y)?|'
                       r'aug(?:ust)?|sep(?:tember)?|oct(?:ober)?|nov(?:ember)?|dec(?:ember)?)|'
                       r'((?:this|last) (?:month|year))', query_str)
        if ma:
            now = datetime.now()
            if ma.group(1):
                month_name = ma.group(1).capitalize()
                if len(month_name) == 3:
                    month_beg = month_end = list(calendar.month_abbr).index(month_name)
                else:
                    month_beg = month_end = list(calendar.month_name).index(month_name)
                year = now.year
                day_end = calendar.monthrange(year, month_end)[1]
            else:
                if 'last' in ma.group(2):
                    if 'year' in ma.group(2):  # last year
                        year = now.year - 1
                        month_beg = 1
                        month_end = 12
                        day_end = 31
                    else:  # last month
                        year = now.year
                        month_beg = month_end = now.month - 1
                        day_end = calendar.monthrange(year, month_end)[1]
                else:
                    if 'year' in ma.group(2):  # this year
                        month_beg = 1
                        month_end = now.month
                    else:  # this month
                        month_beg = month_end = now.month
                    day_end = now.day
                    year = now.year

            params['after'] = datetime(year, month_beg, 1, 0, 0, 0).timestamp()
            params['before'] = datetime(year, month_end, day_end,
                                        23, 59, 59).timestamp()

        # Get activity type.
        # This is a mandatory field. There must be a match.
        ma = re.search(r'(run|ride|walk)s?', query_str)

        params['type'] = ma.group(1).capitalize()

        return params

    def resolve_query(self, query_str):
        """Parse query and get corresponding stats."""
        params = self.parse_query(query_str)

        # Get activities.
        activities = Strava.get_activities(self.auth, params)

        if len(activities) == 0:
            logging.warning("There are no activites that matched your query: %s\n", query_str)
            return

        print()
        for act in activities:
            Strava.print_activity(act)
            print()
