#!/usr/bin/python
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
	#print url
	soup = BeautifulSoup.BeautifulSoup(html)
	ss = soup.findAll('table', 'article')
	for s in ss:
		try:
			rr = {}
			suname = s.find('span', attrs={'class':'u-name'}).find('a')
			rr['uname'] = suname.renderContents()
			scontext = s.find('td', attrs={'class':"a-content a-no-bottom a-no-top"})
			datestr = re.search('发信站: 北邮人论坛 \((.*?)\),',str(scontext)).group(1)
			datestr = datestr.replace('&nbsp;',' ')
			date = datetime.datetime.strptime(datestr ,'%a %b %d %H:%M:%S %Y')
			context = scontext.renderContents()
			#print context
			context = re.sub(r'.*站内 <br />&nbsp;&nbsp;<br />', "", context)
			context = re.sub(r'<br /> -- <br />&nbsp;&nbsp;<br /> <font.*', '', context)
			context = re.sub(r'【 在.*?的大作中提到: 】', '', context)
			context = re.sub(r'<font.*?>.*</font>', '', context)
			context = re.sub(r'<br />', '', context)
			context = re.sub(r'&nbsp;', ' ', context)
			context = re.sub(r'<img .*? />', ' ', context)
			context = re.sub(r'</p>', '', context)
			#print context
			rr['context'] = context
			rr['post_time'] = str(date)
			r.append(rr)
		except:
			pass
	if pageno == 1:
		ms = re.findall(r'\?p=(\d*)', html)
		max_p = 0
		for m in ms:
			max_p = max(max_p, int(m))
		print max_p
		for pno in range(2,max_p+1):
			r.extend(getArtical(board, id, pno))
	return r
def downloadBoard(board,pageno):
	ps = getIndexPage(board,pageno)
	print ps
	for a in ps:
		for i in range(3):
			try:
				article = {'id':a['id'], 'title':a['topic']}
				article['posts'] =  getArtical(board, a['id'])
				article['post_time'] = article['posts'][0]['post_time']
				print "ID:%s\tPost:%s\tChar:%s\tTitle:%s" % (a['id'], len(article), 0, a['topic'])
				conn.execute("delete from article where id='%s'" % a['id'])
				sqlstr = "insert into article(id,post_time,len,posts) values('%s','%s','%s','%s')" % (a['id'],article['post_time'], len(article),json.dumps(article))
				#print sqlstr
				conn.execute(sqlstr)
				conn.commit()
				break
			except Exception,ex:
				print ex
def main():
	for i in range(1,25):
		downloadBoard('Job', i)
if __name__ == '__main__':
	main()
	 
