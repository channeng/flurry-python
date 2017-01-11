from datetime import datetime


def stringify_list(list):
    str_list = str(list).replace("[", "").replace("]", "").replace("'", "")
    return str_list

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

# def get_countries():
#     from datetime import timedelta
#     from flurry import Flurry_api

#     month_current = datetime.strftime(datetime.now(), "%Y-%m")
#     month_three_ago = datetime.strftime(datetime.now() - timedelta(weeks=12), "%Y-%m")

#     flurry = Flurry_api(month_three_ago, month_current)
#     results = flurry.get_app_metric("appUsage", "month", ['country'], ['sessions'])

#     countries = {}
#     for row in results:
#         print row
#         countries[str(row["country|iso"])] = {
#             "name": str(row["country|name"]),
#             "id": str(row["country|id"]),
#         }

#     return countries
