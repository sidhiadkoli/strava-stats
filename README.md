# strava-stats
Get detailed activity statistics for a Strava athlete.

## Supported queries.

### Activity type.
The following activity types are supported: `run`, `ride`, and `walk`.

The activity type is mandatory in the query. The type can be pluralized.

The smallest valid query is: `run`

### Performance attributes.
You can get `fastest`, `longest`, or `max elevation` (gain) for an activity type. This returns a single activity that
satisfies the performance metric. If you want the top n activities, then the metric can be preceeded by a number.

Sample queries:
```
3 longest rides
max elevation run
```

### Time range.
You can specify the time range you want to retrieve activities from. Valid terms are month names (Eg: `January` or `jan`) and `this`/`last` `month`/`year`.

If no time is specified, then it is assumed to be over all time.

Sample queries:
```
fastest run last month
longest walk jan
```

### Distance filter.
You can filter activities based on their length. So you can query for activities longer than, for example, `10k` where `k` stands for kilometer. `century` can be used as a subtitute for `100k`.

Sample queries:
```
5k runs this month
fastest century ride
```

### Aggregation.
You can request for `total` followed by an optional `distance`, `time` or `elevation`. If the optional parameter is not provided, then a count of activities that satisfy the query are printed.

Sample queries:
```
total runs this year
total 50k rides
```

### All stats.
Instead of getting each aggregate stat separately, you can request for all stats: total distance, time and elevation gain, and total number of activities of certain milestone distances (eg: 50k for rides).

Sample queries:
```
ride stats this month
```

## Notes:
- The queries are case insensitive.
- The order of each of the above sections in the query doesn't matter. Eg: `fastest 5k run this year` is the same as `run 5k fastest this year`.
- For `fastest`, moving speed is considered for rides and elapsed speed for runs and walks.
