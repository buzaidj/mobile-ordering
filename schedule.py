import datetime

# Open times in 24hr time
#   ex: ("10:30", "14:00")
#
# Change ranges below

LUNCH_ORDERS_RANGE = ("10:30", "13:50")
LUNCH_SERVED_RANGE = ("11:00", "14:00")

DINNER_ORDERS_RANGE = ("17:30", "18:50")
DINNER_SERVED_RANGE = ("17:45", "19:00")

# for testing purposes only around printing tickets
KITCHEN_OPEN = ("10:30", "20:00")


def get_datetime_range(range):
    range_dt = []
    for date_time_str in range:
        dt_obj = datetime.datetime.strptime(date_time_str, '%H:%M')
        range_dt.append(dt_obj.time())

    return tuple(range_dt)

Schedule = {
    "lunch_orders_range": get_datetime_range(LUNCH_ORDERS_RANGE),
    "lunch_served_range": get_datetime_range(LUNCH_SERVED_RANGE),
    "dinner_orders_range": get_datetime_range(DINNER_ORDERS_RANGE),
    "dinner_served_range": get_datetime_range(DINNER_SERVED_RANGE),
    "kitchen_open": get_datetime_range(KITCHEN_OPEN)
}
