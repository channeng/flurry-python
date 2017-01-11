import os

from flurry import Flurry_api, tables
from utils import validate_datetime


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

    # Country filter is buggy
    # str_country_code = raw_input("Please enter comma-separated country codes of countries to filter for (Press Enter to skip):\n> ")
    # if str_country_code:
    #     country_codes = str_country_code.replace(" ", "").split(",")
    # else:
    #     country_codes = []
    # print
    country_codes = []

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
