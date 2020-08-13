import datetime

# Open times in 24hr time
#   ex: ("10:30", "14:00")
#
# Make a set of all the days as integers where monday is 0 and sunday is 6
# Change ranges below

LUNCH_ORDERS_RANGE = ("10:30", "13:50")
LUNCH_DAYS = {6, 0, 1, 2, 3, 4}
LUNCH_SERVED_RANGE = ("11:00", "14:00")

DINNER_ORDERS_RANGE = ("17:30", "18:50")
DINNER_DAYS = {6, 0, 1, 2, 3, 4}
DINNER_SERVED_RANGE = ("17:45", "19:00")

# for testing purposes only around printing tickets
KITCHEN_OPEN = ("00:00", "23:59")
KITCHEN_DAYS = {6, 0, 1, 2, 3, 4, 5}

TEST = ("11:28", "11:30")
TEST_DAYS = {6, 0, 1, 2, 3, 4, 5}

TEST_FULL = ("00:00", "23:59")


def get_datetime_range(range):
    range_dt = []
    for date_time_str in range:
        dt_obj = datetime.datetime.strptime(date_time_str, '%H:%M')
        range_dt.append(dt_obj.time())

    return tuple(range_dt)

class OrderTimes:
    def __init__(self, str_order_range, str_serve_range, int_weekdays):
        self.order_range = get_datetime_range(str_order_range)
        self.serve_range = get_datetime_range(str_serve_range)
        self.weekdays = int_weekdays

Schedule = {
    "lunch_range": OrderTimes(LUNCH_ORDERS_RANGE, LUNCH_SERVED_RANGE, LUNCH_DAYS),
    "dinner_range": OrderTimes(DINNER_ORDERS_RANGE, DINNER_SERVED_RANGE, DINNER_DAYS),
    "kitchen_open": OrderTimes(KITCHEN_OPEN, KITCHEN_OPEN, KITCHEN_DAYS),
    "test_full": OrderTimes(TEST_FULL, TEST_FULL, TEST_DAYS)
}
