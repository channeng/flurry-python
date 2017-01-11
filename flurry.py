import os
import time
from datetime import datetime
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


def stringify_list(list):
    str_list = str(list).replace("[", "").replace("]", "").replace("'", "")
    return str_list


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

                if filter_countries:
                    country_dict = get_countries()
                    country_set = set(country_dict)
                    filter_country_set = set(filter_countries)
                    if filter_country_set < country_set:   # If filter countries is a subset of all countries
                        country_ids = [country_dict[country]["id"] for country in filter_countries]
                        get_url = get_url + "&filters=country|id-in" + str(country_ids).replace(" ", "").replace("'", "")
                    else:
                        print "The following country codes are invalid: {}".format(filter_country_set - country_set)

                # print "API url:\n{}\n".format(get_url)
                time.sleep(1)
                response = requests.get(get_url, headers=self.headers)

                if response.status_code == 200:
                    results = response.json()
                    return results["rows"]
                else:
                    print "Response failed with status: {}".format(response.status_code)
                    print "Error description: {}".format(response.json()["description"])


def get_countries():
    from datetime import timedelta

    month_current = datetime.strftime(datetime.now(), "%Y-%m")
    month_three_ago = datetime.strftime(datetime.now() - timedelta(weeks=12), "%Y-%m")

    flurry = Flurry_api(month_three_ago, month_current)
    results = flurry.get_app_metric("appUsage", "month", ['country'], ['sessions'])

    countries = {}
    for row in results:
        countries[str(row["country|iso"])] = {
            "name": str(row["country|name"]),
            "id": str(row["country|id"]),
        }

    return countries


def validate_datetime(date_text):
    try:
        datetime.strptime(date_text, '%Y-%m-%dT%H')
        return date_text, 1
    except ValueError:
        try:
            datetime.strptime(date_text, '%Y-%m-%d')
            return date_text, 2
        except ValueError:
            try:
                datetime.strptime(date_text, '%Y-%m')
                return date_text, 3
            except ValueError:
                print "Incorrect data format, should be in the following formats:\n(1) YYYY-MM-DDTHH\n(2) YYYY-MM-DD\n(3) YYYY-MM"
                return date_text, None


def interface(generate_code_only=False):
    os.system("clear")
    start, start_datetype = validate_datetime(raw_input("Format for Day, Week: YYYY-MM-DD\nFormat for Month    : YYYY-MM\nFormat for Hour     : YYYY-MM-DDTHH\n\nPlease enter start date:\n> "))
    print
    while start_datetype == None:
        start, start_datetype = validate_datetime(raw_input("Format for Day, Week: YYYY-MM-DD\nFormat for Month    : YYYY-MM\nFormat for Hour     : YYYY-MM-DDTHH\n\nPlease enter start date:\n> "))
        print

    end, end_datetype = validate_datetime(raw_input("Please enter end date:\n> "))
    print
    while end_datetype == None:
        end, end_datetype = validate_datetime(raw_input("Please enter end date:\n> "))
        print

    while start_datetype != end_datetype:
        print "Start and end date types are not the same. Please try again.\n"
        start, start_datetype = validate_datetime(raw_input("Format for Day, Week: YYYY-MM-DD\nFormat for Month    : YYYY-MM\nFormat for Hour     : YYYY-MM-DDTHH\n\nPlease enter start date:\n> "))
        print
        end, end_datetype = validate_datetime(raw_input("Please enter end date:\n> "))
        print

    table_choices = tables.keys()
    len_table_choices = len(table_choices)
    str_table_choices = ""
    for i, t in enumerate(table_choices):
        str_table_choices += "({0}) {1}\n".format(i + 1, t)
    table_num = int(raw_input("Please choose one of the following:\n{}> ".format(str_table_choices)))
    while table_num > len_table_choices or table_num < 1:
        print "Please choose a number between 1 and {}".format(len_table_choices)
        table_num = int(raw_input("Please choose one of the following:\n{}> ".format(str_table_choices)))
    table_index = table_num - 1
    table = table_choices[table_index]
    print

    time_grain_choices = tables[table]["time_grain"]
    len_time_grain_choices = len(time_grain_choices)
    str_time_grain_choices = ""
    for i, t in enumerate(time_grain_choices):
        str_time_grain_choices += "({0}) {1}\n".format(i + 1, t)
    time_grain_num = int(raw_input("Please choose one of the following:\n{}> ".format(str_time_grain_choices)))
    while table_num > len_table_choices or table_num < 1:
        print "Please choose a number between 1 and {}".format(len_time_grain_choices)
        time_grain_num = int(raw_input("Please choose one of the following:\n{}> ".format(str_time_grain_choices)))
    time_grain_index = time_grain_num - 1
    time_grain = time_grain_choices[time_grain_index]
    print

    dimensions_choices = tables[table]["dimensions"]
    str_dimensions_choices = ""
    for i, t in enumerate(dimensions_choices):
        str_dimensions_choices += "({0}) {1}\n".format(i + 1, t)
    dimensions_num = raw_input("Please select 1 or more of the following (comma-separated):\n{}> ".format(str_dimensions_choices))
    dimensions_index = [int(num) - 1 for num in dimensions_num.replace(" ", "").split(",")]
    dimensions = [dimensions_choices[index] for index in dimensions_index]
    print

    metrics_choices = tables[table]["metrics"]
    str_metrics_choices = ""
    for i, t in enumerate(metrics_choices):
        str_metrics_choices += "({0}) {1}\n".format(i + 1, t)
    metrics_num = raw_input("Please select 1 or more of the following (comma-separated):\n{}> ".format(str_metrics_choices))
    metrics_index = [int(num) - 1 for num in metrics_num.replace(" ", "").split(",")]
    metrics = [metrics_choices[index] for index in metrics_index]
    print

    str_country_code = raw_input("Please enter comma-separated country codes of countries to filter for (Press Enter to skip):\n> ")
    if str_country_code:
        country_codes = str_country_code.replace(" ", "").split(",")
    else:
        country_codes = []
    print

    # Execute query
    print "Code snippet:\n----------------------------------------------\n"
    print """from flurry import Flurry_api\n\nflurry = Flurry_api("{0}", "{1}")\nresults = flurry.get_app_metric("{2}", "{3}", {4}, {5}, filter_countries={6})\n
    """.format(start, end, table, time_grain, dimensions, metrics, country_codes)

    if not generate_code_only:
        flurry = Flurry_api(start, end)
        results = flurry.get_app_metric(table, time_grain, dimensions, metrics, filter_countries=country_codes)
        return results


if __name__ == "__main__":
    interface(generate_code_only=True)
