import calendar
from datetime import datetime
import logging

from authenticate import Auth
from strava import Strava


class Stats:
    """Get requested statistics of the user's activities."""
    def __init__(self):
        self.auth = Auth()

    def parse_query(self, query_str):
        """Parse the requested query."""
        # TODO: Do something better than string matching.
        query_tokens = query_str.split(' ')

        params = {}

        # Max filter.
        if 'longest' in query_tokens:
            params['filter_attr'] = 'distance'
            params['count'] = 1
        elif 'fastest' in query_tokens:
            params['filter_attr'] = 'speed'
            params['count'] = 1

        # Distance filter.
        if '5k' in query_tokens:
            params['distance'] = 5 * 1000
        elif '10k' in query_tokens:
            params['distance'] = 10 * 1000
        elif '50k' in query_tokens:
            params['distance'] = 50 * 1000
        elif 'century' in query_tokens or '100k' in query_tokens:
            params['distance'] = 100 * 1000

        # Get time frame.
        if 'last month' in query_str:
            now = datetime.now()
            month_length = calendar.monthrange(now.year, now.month - 1)[1]
            params['after'] = datetime(now.year, now.month - 1, 1, 0, 0, 0).timestamp()
            params['before'] = datetime(now.year, now.month - 1, month_length,
                                        23, 59, 59).timestamp()
        elif 'this month' in query_str:
            now = datetime.now()
            params['after'] = datetime(now.year, now.month, 1, 0, 0, 0).timestamp()
        elif 'this year' in query_str:
            now = datetime.now()
            params['after'] = datetime(now.year, 1, 1, 0, 0, 0).timestamp()
        else:
            # Default is all-time.
            pass

        # Get activity type.
        if 'run' in query_tokens:
            params['type'] = Strava.Type.run
        elif 'ride' in query_tokens:
            params['type'] = Strava.Type.ride

        return params

    def resolve_query(self, query_str):
        """Parse query and get corresponding stats."""
        params = self.parse_query(query_str)

        # Get activities.
        activities = Strava.get_activities(self.auth, params)

        if len(activities) == 0:
            logging.warning("There are no activites that matched your query: %s", query_str)
            return

        print()
        for act in activities:
            Strava.print_activity(act)
            print()
