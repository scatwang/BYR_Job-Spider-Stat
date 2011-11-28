#!/usr/bin/python
# -*- coding: utf-8 -*-

import datetime
import sqlite3
import json
import re
conn = sqlite3.connect('byr.db')
stat = {}
words = {}
def load_conf():
	f = open('stat.conf')
	for line in f:
		print line,
		items = line.strip().split(' ')
		words[items[0]] = re.compile(items[1].decode('utf8'), re.I)
def record_words(word_set, date, count=1):
	for word in word_set:
		record(word,date,count)
def record(word, date, count=1):
	if date.year <2011 and date.month <=8: 
		return	
	date = date.strftime("%Y%m.%d")
	date = date[4:9]
	#date = date[4:8] + '0'
	if not stat.has_key(word):
		stat[word] = {}
	if not stat[word].has_key(date):
		stat[word][date] = 0
	stat[word][date] += count
	
def stat_article(article):
	r = set()
	date = datetime.datetime.strptime( article['post_time'], '%Y-%m-%d %H:%M:%S' )
	date = date.date()
	r =  stat_string(article['title'])

	s = set(r)
	record_words(s, date, 3)
	for post in article['posts']:
		s.union(stat_post(post, set(r)))
	return s

def stat_string(s):
	current_words = set()
	for word_key in words:
		if words[word_key].search(s):
			current_words.add(word_key)
	return current_words
def stat_post(post, current_words):			
	current_words.union(stat_string(post['context']))
	date = datetime.datetime.strptime( post['post_time'], '%Y-%m-%d %H:%M:%S' )
	date = date.date()
	record_words(current_words, date)
	return current_words

def main():
	load_conf()
	cur = conn.cursor()
	cur.execute('select posts, id from article ')
	data = cur.fetchall()
	for post in data:
		j = None
		try:
			print post[1], "\r",
			j = json.loads(post[0])
		except:
			#print json.dumps(j, indent=3, ensure_ascii=False)
			pass
		if j:
			stat_article(j)
		
	#print json.dumps(stat,indent=3,ensure_ascii=False)
	print 
	f = open('/var/www/html/byrjob.json','w')
	date_label = []
	date = datetime.date(2011,10,1)
	while date < datetime.date.today():
		k = date.strftime('%m.%d') 
		date_label.append(k)
		date += datetime.timedelta(days=1)

	j = {}
	for word in stat:
		c = 0
		j[word]=[]
		for date in stat[word]:
			c += stat[word][date]
		print word, c
		for k in date_label:
				v = 0
				if stat[word].has_key(k): v = stat[word][k]
				j[word].append(v)
	j = {'data':j,'label':date_label}
	print json.dumps(j,ensure_ascii=False)
	f.write(json.dumps(j))
	f.close()	
if __name__=='__main__':
	main()
