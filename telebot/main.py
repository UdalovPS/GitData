from datetime import datetime, timedelta

data_1 = datetime(2022, 12, 31)
print(type(data_1.year))
#
# data_2 = datetime(2023, 1, 1)
#
# delta = (data_2-data_1)
# print(type(delta.days))

date_1 = data_1.date()
time_1 = data_1.time()
print(date_1)
print(time_1)

print(datetime.combine(date_1, time_1))


dd = {datetime.now(): 1}
print(dd)
