import os
import time
from utils import stringify_list
import requests
try:
    import urlparse
    from urllib import urlencode
except:     # For Python 3
    import urllib.parse as urlparse
    from urllib.parse import urlencode

flurry_token = os.environ["FLURRY_TOKEN"]
tables = {
    "appUsage": {
        "time_grain": ['day', 'week', 'month', 'all'],
        "dimensions": ["company", "app", "appVersion", "country", "language", "region", "category"],
        "metrics": ["sessions", "activeDevices", "newDevices", "timeSpent", "averageTimePerDevice", "averageTimePerSession"]
    },
    "appEvent": {
        "time_grain": ['day', 'week', 'month', 'all'],
        "dimensions": ["company", "app", "appVersion", "country", "language", "region", "category", "event", "paramName", "paramValue"],
        "metrics": ["activeDevices", "newDevices", "timeSpent", "averageTimePerDevice", "averageTimePerSession", "occurrences"]
    },
    "realtime": {
        "time_grain": ['hour', 'day', 'all'],
        "dimensions": ["company", "app", "appVersion", "country"],
        "metrics": ["sessions", "activeDevices"]
    }
}


class Flurry_api(object):
    def __init__(self, start, end):
        """
        Format for Day, Week: YYYY-MM-DD
        Format for Month    : YYYY-MM
        Format for Hour     : YYYY-MM-DDTHH
        """
        self.start_date = start
        self.end_date = end
        self.headers = {'Authorization': 'Bearer ' + flurry_token}
        self.base_url = "https://api-metrics.flurry.com/public/v1/data/"
        # self.events_api_url = urlparse.urljoin(base_url, "realtime")

    def get_app_metric(self, table, time_grain, dimensions, metrics, filter_countries=[]):
        """
        app_metric must be one of the following:
        ActiveUsers, NewUsers, MedianSessionLength, AvgSessionLength,
        Sessions, RetainedUsers, PageViews, AvgPageViewsPerSession

        For more information, please see:
        https://developer.yahoo.com/flurry/docs/api/code/appmetrics/

        """
        choice_tables = tables.keys()
        if table not in choice_tables:
            str_choice_tables = stringify_list(choice_tables)
            print """{0} is not a valid table.\n\nPlease choose 1 or more of the following:\n{1}
            """.format(table, str_choice_tables)
        else:
            choice_time_grain = tables[table]["time_grain"]
            choice_dimensions = tables[table]["dimensions"]
            choice_metrics = tables[table]["metrics"]
            if time_grain not in choice_time_grain:
                str_choice_time_grain = stringify_list(choice_time_grain)
                print """{0} is not a valid time grain for {1}.\n\nPlease choose 1 or more of the following:\n{2}
                """.format(time_grain, table, str_choice_time_grain)
            elif not(set(dimensions) < set(choice_dimensions)):
                str_choice_dimensions = stringify_list(choice_dimensions)
                print """{0} is not a valid dimension for {1}.\n\nPlease choose 1 or more of the following:\n{2}
                """.format(stringify_list(dimensions), table, str_choice_dimensions)
            elif not(set(metrics) < set(choice_metrics)):
                str_choice_metrics = stringify_list(choice_metrics)
                print """{0} is not a valid metric for {1}.\n\nPlease choose 1 or more of the following:\n{2}
                """.format(stringify_list(metrics), table, str_choice_metrics)
            else:
                # API url construction and query
                dimensions_chosen = [dimension for dimension in choice_dimensions if dimension in dimensions]
                params = [table, time_grain] + dimensions_chosen
                get_url = self.base_url
                for param in params:
                    get_url = urlparse.urljoin(get_url, param + "/")
                get_url = get_url[:-1]

                str_metrics_chosen = stringify_list([metric for metric in choice_metrics if metric in metrics]).replace(" ", "")
                get_url = get_url + "?metrics=" + str_metrics_chosen + "&dateTime=" + self.start_date + "/" + self.end_date

                # country filters is still buggy
                # if filter_countries:
                    # country_dict = get_countries()
                    # country_set = set(country_dict)
                    # filter_country_set = set(filter_countries)
                    # if filter_country_set < country_set:   # If filter countries is a subset of all countries
                    #     country_ids = [country_dict[country]["id"] for country in filter_countries]
                    #     get_url = get_url + "&filters=country|id-in" + str(country_ids).replace(" ", "").replace("'", "")
                    # else:
                    #     print "The following country codes are invalid: {}".format(filter_country_set - country_set)

                print "API url:\n{}\n".format(get_url)
                time.sleep(1)
                response = requests.get(get_url, headers=self.headers)

                if response.status_code == 200:
                    results = response.json()
                    return results["rows"]
                else:
                    print "Response failed with status: {}".format(response.status_code)
                    print "Error description: {}".format(response.json()["description"])
