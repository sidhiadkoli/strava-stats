import requests


class Strava:
    # Constant strings.
    class Type:
        ride = 'Ride'
        run = 'Run'

    def filter_activities(activities, params):
        """Returns a list of activities filtered by the given parameters."""
        activities = [act for act in activities if act['type'] == params['type']]

        if 'filter_attr' in params:
            if params['filter_attr'] == 'distance':
                def func(a): return a['distance']
            elif params['filter_attr'] == 'speed':
                # Get fastest activity first.
                # Note that we are computing using elapsed time.
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

    def get_activities(auth, params):
        """Gets all activities of the authenticated user in an optional time range."""
        query_params = {}
        if 'before' in params:
            query_params['before'] = params['before']
        if 'after' in params:
            query_params['after'] = params['after']

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

        if act['type'] == Strava.Type.ride:
            print('Moving speed: '
                  f"{Strava.format_speed(act['distance'], act['moving_time'])}")
            print('Elapsed speed: '
                  f"{Strava.format_speed(act['distance'], act['elapsed_time'])}")
        else:
            print('Moving pace: '
                  f"{Strava.format_pace(act['distance'], act['moving_time'])}")
            print('Elapsed pace: '
                  f"{Strava.format_pace(act['distance'], act['elapsed_time'])}")
        print(f"Elevation gain: {round(act['total_elevation_gain'])}m")
