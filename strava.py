from datetime import datetime
import time

import requests


class Strava:
    # Constant strings.
    class Type:
        ride = 'Ride'
        run = 'Run'
        walk = 'Walk'

    # Cache queried activities and their corresponding date ranges.
    _activities_cache = []
    _date_ranges = []

    def _remove_dups(activities):
        """Removes duplicate activities in sorted list."""
        prev = None
        uniq_activities = []
        for a in activities:
            if a['id'] != prev:
                uniq_activities.append(a)
                prev = a['id']
        return uniq_activities

    def filter_activities(activities, params):
        """Returns a list of activities filtered by the given parameters."""
        activities = [act for act in activities if act['type'] == params['type']]

        if 'filter_attr' in params:
            if params['filter_attr'] == 'distance':
                def func(a): return a['distance']
            elif params['filter_attr'] == 'speed':
                # Get fastest activity first.
                # Note that we are computing using elapsed time for runs/walks
                # and moving time for rides.
                if params['type'] == Strava.Type.ride:
                    def func(a): return a['distance'] / a['moving_time']
                else:
                    def func(a): return a['distance'] / a['elapsed_time']
            else:  # elevation
                def func(a): return a['total_elevation_gain']
            activities = sorted(activities,
                                key=func,
                                reverse=True)

        if 'distance' in params:
            activities = list(filter(lambda a: a['distance'] > params['distance'], activities))

        if 'count' in params:
            activities = activities[:params['count']]

        return activities

    def get_activity_timestamp(activity):
        """Get a datetime object of the activity's start time."""
        datetime_str = activity['start_date_local'][:-1]  # Ignore the Z at the end.
        return datetime.timestamp(datetime.fromisoformat(datetime_str))

    def get_activities(auth, params):
        """Gets all activities of the authenticated user in an optional time range."""
        query_params = {}
        if 'before' in params:
            query_params['before'] = params['before']
        if 'after' in params:
            query_params['after'] = params['after']

        # Check if we have cached the activities in the requested date range.
        if '*' in Strava._date_ranges:
            # The cache contains all activities.
            after = params.get('after', Strava.get_activity_timestamp(Strava._activities_cache[0]))
            before = params.get('before', time.time())
            activities = [a for a in Strava._activities_cache
                          if (after <= Strava.get_activity_timestamp(a) and
                              before >= Strava.get_activity_timestamp(a))]
        elif 'after' in params:
            # Check if the 'before' and 'after' datetimes are within a date range.
            after = params['after']
            before = params.get('before', time.time())
            dr = [(date[0], date[1])
                  for date in Strava._date_ranges if after >= date[0] and before <= date[1]]
            if len(dr) > 0:
                activities = [a for a in Strava._activities_cache
                              if (after <= Strava.get_activity_timestamp(a) and
                                  before >= Strava.get_activity_timestamp(a))]

        if 'activities' not in locals():
            # We don't have the requested activities cached. Get it from server.
            activities = []
            page = 1
            while True:
                query_params['page'] = page
                res = requests.get('https://www.strava.com/api/v3/athlete/activities',
                                   params=query_params,
                                   headers={'Authorization': f"Bearer {auth.access_token}"})
                res.raise_for_status()
                if len(res.json()) == 0:
                    break

                activities += res.json()
                page += 1

            # Update cache.
            Strava._activities_cache.extend(activities)
            Strava._activities_cache.sort(key=lambda a: Strava.get_activity_timestamp(a))
            Strava._activities_cache = Strava._remove_dups(Strava._activities_cache)

            # Update date range list.
            if 'after' not in params and 'before' not in params:
                # We have all stats. No need to store date range.
                Strava._date_ranges = ['*']
            elif 'after' in params:
                if 'before' not in params:
                    before = datetime.now()
                    before.replace(hour=23, minute=59, second=59)
                    before = datetime.timestamp(before)
                else:
                    before = params['before']
                Strava._date_ranges.append((params['after'], before))

        return Strava.filter_activities(activities, params)

    def format_speed(distance, time):
        """Format speed in km/hr."""
        speed = distance / time * 60 * 60 / 1000
        return f"{round(speed, 2)}km/hr"

    def format_pace(distance, time):
        """Format pace in min/km"""
        pace = time / distance * 1000 / 60
        pace_min = int(pace)
        pace_sec = int((pace - int(pace)) * 60)
        return f"{pace_min}:{pace_sec}min/km"

    def print_activity(act):
        print(f"Name: {act['name']}")
        print(f"Type: {act['type']}")
        print(f"Date: {act['start_date_local']}")
        print(f"Distance: {round(act['distance']/1000, 2)}km")

        if act['type'] == Strava.Type.run:
            print('Moving pace: '
                  f"{Strava.format_pace(act['distance'], act['moving_time'])}")
            print('Elapsed pace: '
                  f"{Strava.format_pace(act['distance'], act['elapsed_time'])}")
        else:
            print('Moving speed: '
                  f"{Strava.format_speed(act['distance'], act['moving_time'])}")
            print('Elapsed speed: '
                  f"{Strava.format_speed(act['distance'], act['elapsed_time'])}")
        print(f"Elevation gain: {round(act['total_elevation_gain'])}m")
