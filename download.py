#!/usr/bin/env python
import os
import urllib
import datetime

url = 'http://www.data.jma.go.jp/obd/stats/etrn/view/hourly_s1.php?'

if __name__ == '__main__':
	date = datetime.datetime(1990, 1, 1)

	while date < datetime.datetime(2000, 1, 1):
		try:
			params = {'prec_no': 62, 'block_no': 47772, 'year': date.year, 'month': date.month, 'day': date.day}
			html = urllib.urlopen(url + urllib.urlencode(params))
			open(os.path.join('data', '%04d' % date.year, date.strftime('%Y-%m-%d.html')), 'w').write(html.read())
		except:
			print date

		date += datetime.timedelta(days = 1)
