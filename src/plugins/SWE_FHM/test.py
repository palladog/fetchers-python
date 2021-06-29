from datetime import date, datetime, timedelta

d = '2021-26'
r = datetime.strptime(d + '-0', '%Y-%W-%w') # Gets the Sunday date of the week
#print(r)

today = date.today()
year = today.year
week = today.isocalendar()[1]
#print(year)
#print(week)

#ddate = (today - date(2020, 3, 5)).days
#print (ddate)

#theweek = date(2020, 1, 5).isocalendar()[1]
#print("week", theweek)

#next_sunday = datetime.strptime(today + '-0', '%Y-%W-%w')
#week_difference = datetime.timedelta(7)
#last_sunday = next_sunday - week_difference
#print(last_sunday)

#idx = (day.weekday() + 1) % 7 # MON = 0, SUN = 6 -> SUN = 0 .. SAT = 6
#print(idx)
#last_sunday = day - timedelta(7+idx-7)
#print(last_sunday)
day = datetime(2021, 6, 5)
#last_week = day - timedelta(days=7)
#sunday = last_week - timedelta(days=last_week.weekday()) + timedelta(days=6)

next_sunday = datetime.strptime(day.strftime('%Y-%W') + '-0', '%Y-%W-%w')

print(next_sunday)