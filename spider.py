#!/usr/local/python2.7/bin/python
# -*- coding: utf-8 -*-

import re
import urllib2
import BeautifulSoup
import json
import sqlite3
import datetime

conn = sqlite3.connect('byr.db')
def getIndexPage(board,pageno):
	r = []
	url = 'http://bbs.byr.cn/board/%s?p=%s' % (board, pageno)
	html = urllib2.urlopen(url).read()
	soup = BeautifulSoup.BeautifulSoup(html)
	stb = soup.find('table', 'board-list tiz')
	strs = stb.findAll('tr')
	for tr in strs:
		if tr.has_key('class') and tr['class'].find('top') >= 0: continue # skip top topics
		td = tr.find('td', 'title_9')
		id = re.search(r'/article/Job/(\d*)',str(td)).group(1)
		topic = td.find('a').renderContents()
		r.append({'id':id, 'topic':topic})
	return r
def getArtical(board,id,pageno=1):
	r = []
	url = 'http://bbs.byr.cn/article/%s/%s' % (board, id)
	if pageno <> 1:
		url += '?p=%d' % pageno
	html = urllib2.urlopen(url).read()
	print url
	soup = BeautifulSoup.BeautifulSoup(html)
	ss = soup.findAll('table', 'article')
	for s in ss:
		rr = {}
		suname = s.find('span', attrs={'class':'u-name'}).find('a')
		rr['uname'] = suname.renderContents()
		scontext = s.find('td', attrs={'class':"a-content a-no-bottom a-no-top"})
		datestr = re.search('发信站: 北邮人论坛 \((.*?)\),',str(scontext)).group(1)
		date = datetime.datetime.strptime(datestr ,'%a %b %d %H:%M:%S %Y')
		scontext = scontext[scontext.find('站内 <br />&nbsp;&nbsp;<br />'):]
		rr['context'] = str(scontext)
		rr['post_time'] = str(date)
		r.append(rr)
	if pageno == 1:
		ms = re.findall(r'\?p=(\d*)', html)
		max_p = 0
		for m in ms:
			max_p = max(max_p, int(m))
		print max_p
		for pno in range(2,max_p+1):
			r.extend(getArtical(board, id, pno))
	return r
def main():
	ps = getIndexPage('Job',1)
	print ps
	for a in ps:
		article = {'id':a['id'], 'title':a['topic']}
		article['posts'] =  getArtical('Job', a['id'])
		article['post_time'] = article['posts'][0]['post_time']
		print "ID:%s\tPost:%s\tChar:%s\tTitle:%s" % (a['id'], len(article), 0, a['topic'])
		conn.execute("delete from article where id='%s'" % a['id'])
		conn.execute("insert into article(id,len,posts) value('%s','%s','%s')" % (a['id'], len(article),json.dumps(article)))
		conn.commit()

if __name__ == '__main__':
	main()
	 
