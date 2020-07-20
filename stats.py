import calendar
from datetime import datetime
import logging
import re

from authenticate import Auth
from strava import Strava


class Stats:
    marathon = 42.195
    milestones = {Strava.Type.run: [5, 10, marathon/2, marathon],
                  Strava.Type.walk: [5, 10],
                  Strava.Type.ride: [50, 100]}

    """Get requested statistics of the user's activities."""
    def __init__(self):
        self.auth = Auth()

    def parse_query(self, query_str):
        """Parse the requested query."""
        # TODO: Do something better than string matching.

        params = {}

        # After parsing each section, remove that section from the string to
        # prevent accidental regex errors because of string match.

        # Max filter.
        ma = re.search(r'([0-9]* ?)(longest|fastest|max elevation)', query_str)
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
            query_str = query_str.replace(ma.group(0), '', 1)

        # User can request for general stats or aggregate stats. Both simulataneously
        # doesn't make sense.

        # General stats.
        ma = re.search(r'\bstats\b', query_str)
        if ma:
            params['total'] = ['count', 'distance', 'time', 'elevation']
            params['stats'] = True
            query_str = query_str.replace(ma.group(0), '', 1)

        # Aggregate stats.
        ma = re.search(r'total\s?(distance|time|elevation)?', query_str)
        if ma:
            params['total'] = [ma.group(1)] if ma.group(1) else ['count']
            query_str = query_str.replace(ma.group(0), '', 1)

        # Distance filter.
        ma = re.search(r'(([0-9]+)k)|(century|(half |full )?marathon)', query_str)
        if ma:
            if ma.group(0) == 'century':
                dist = 100
            elif 'marathon' in ma.group(0):
                dist = Stats.marathon
                if 'half' in ma.group(0):
                    dist = dist / 2
            else:
                dist = int(ma.group(2))
            params['distance'] = dist * 1000
            query_str = query_str.replace(ma.group(0), '', 1)

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
            query_str = query_str.replace(ma.group(0), '', 1)

        # Get activity type.
        # This is a mandatory field. There must be a match.
        ma = re.search(r'(run|ride|walk)s?', query_str)
        if not ma:
            raise ValueError('Expecting an activity of either run, ride, or walk.')

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
        aggregate = params.get('total')
        if aggregate:
            print('Total stats:')
            for agg in aggregate:
                print(f"{agg.capitalize()}: ", end='')
                if agg == 'count':
                    print(f"{len(activities)}")
                elif agg == 'distance':
                    print(f"{Strava.format_distance(Strava.get_total_distance(activities))}")
                elif agg == 'time':
                    print(f"{Strava.format_time(Strava.get_total_time(activities))}")
                else:  # Total elevation.
                    print(f"{round(Strava.get_total_elevation(activities), 2)}m")

            if params.get('stats'):
                for dist in Stats.milestones[params['type']]:
                    params['distance'] = dist * 1000
                    activities = Strava.get_activities(self.auth, params)
                    if len(activities):  # Print the count only if there are activities.
                        print(f"{dist}k: {len(activities)}")
            print()
        else:
            # Print activity information.
            for act in activities:
                Strava.print_activity(act)
                print()
