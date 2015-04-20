#!/usr/bin/env python
#encoding:utf-8

# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.
#
# Julian Garcia-Sotoca Pascual

import logging
import tornado.escape
import tornado.ioloop
import tornado.options
import tornado.web
import tornado.websocket
from tornado import autoreload
import os.path
import uuid
import datetime
import pyodbc
import re
import os
from pymongo import Connection
from bson.objectid import ObjectId
import json
import time
import tornado.auth

from tornado.options import define, options

define("port", default=8888, help="run on the given port", type=int)

class JSONEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, ObjectId):
            return str(o)
        return json.JSONEncoder.default(self, o)

class BaseHandler(tornado.web.RequestHandler):
    def get_current_user(self):
        user = self.get_secure_cookie("user")
        print "user: %s" % user
        if not user: return None
        return user

class Application(tornado.web.Application):
    def __init__(self):
        handlers = [
            (r"/", MainHandler),
            (r"/events", EventsSocketHandler),
            (r"/full", FullHandler),
            (r"/auth/login/", AuthLoginHandler),
            (r"/auth/logout/", AuthLogoutHandler),
            (r"/a/fulllog", FullAjaxHandler),
            (r"/a/realtime", realtimeAjaxHandler),
            (r"/ajax", Ajax),
			(r"/aja", Aja),
			(r"/ajb", Ajb),
            #(r'/(favicon.ico)', tornado.web.StaticFileHandler, {"path": ""}),
        ]
        settings = dict(
            cookie_secret= "julian",
            template_path=os.path.join(os.path.dirname(__file__), "templates"),
            static_path=os.path.join(os.path.dirname(__file__), "static"),
            login_url="/auth/login/",
            xsrf_cookies=True,
        )
        #logging.info(settings)
        tornado.web.Application.__init__(self, handlers, **settings)

class Ajax(tornado.web.RequestHandler):
	def get_current_user(self):
		return self.get_secure_cookie("user")
		
	@tornado.web.authenticated
	def get(self):
		self.render("ajax.html")
        
class Aja(BaseHandler):
	@tornado.web.authenticated
	def get(self):
		self.write(str(range(1, 10)))
		self.finish()

class Ajb(BaseHandler):
	@tornado.web.authenticated
	def post(self):
		#print 'post ajb'
		#print self.request
		#print self.get_secure_cookie("user")
		time.sleep(1)
		self.write(str(range(10, 20)))
		self.finish()

class realtimeAjaxHandler(BaseHandler):
	@tornado.web.authenticated
	@tornado.web.asynchronous
	def post(self):
		sendEvents(self)
		

class FullAjaxHandler(BaseHandler):
	@tornado.web.authenticated
	@tornado.web.asynchronous
	def post(self):
		#time.sleep(5)
		cachefull=[]
		global domains
		EVENTSPERPAGE=10
		logging.info("[FullHandler] geting %d events. Cache size %d" % (EVENTSPERPAGE, len(cachefull)))
		for e in coll.find().sort( [("id", -1 )] )[0:EVENTSPERPAGE]:
			cachefull.append(e)
			#print e['id']
		self.render("fulllogajax.html", events=cachefull, domains=domains)
		logging.info("[FullAjaxHandler] sent ajax response")
		#self.finish()

class MainHandler(tornado.web.RequestHandler):
	def get_current_user(self):
		return self.get_secure_cookie("user")
	
	@tornado.web.authenticated
	def get(self):
		global domains
		
		username = tornado.escape.xhtml_escape(self.current_user)
		logging.info("[Auth OK] username: %s secure_cookie: %s" % (username, self.get_secure_cookie("user") ))
		self.render("index.html", username=username, events=EventsSocketHandler.cache, domains=domains)

class FullHandler(tornado.web.RequestHandler):
	def get_current_user(self):
		return self.get_secure_cookie("user")
		
	@tornado.web.authenticated
	def get(self):
		cachefull=[]
		global domains
		#logging.info("[FullHandler] Cache size %d" % len(cachefull))
		EVENTSPERPAGE=50
		logging.info("[FullHandler] geting %d events. Cache size %d" % (EVENTSPERPAGE, len(cachefull)))
		for e in coll.find().sort( [("id", -1 )] )[0:EVENTSPERPAGE]:
			cachefull.append(e)
			#print e['id']
		self.render("fulllog.html", events=cachefull, domains=domains)
			

class AuthLoginHandler(tornado.web.RequestHandler):
	def get(self):
		try:
			errormessage = self.get_argument("error")
		except:
			errormessage = ""
		self.render("login.html", errormessage = errormessage)
	
	def check_permission(self, password, username):
		if username == "admin" and password == "admin":
			return True
		return False

	def post(self):
		username = self.get_argument("username", "")
		password = self.get_argument("password", "")
		auth = self.check_permission(password, username)
		if auth:
			self.set_current_user(username)
			self.set_secure_cookie("user", self.get_argument("username"))
			#self.redirect(self.get_argument("next", u"/"))
			self.redirect(u"/")
			logging.info("[REDIRECT] / %s" % username)
			
		else:
			error_msg = u"?error=" + tornado.escape.url_escape("Login incorrect")
			#self.redirect(u"/auth/login/" + error_msg)
			logging.info("[REDIRECT] /auth/login/" + error_msg)
			self.set_secure_cookie("wrong", str(int(wrong)+1))
			self.write('Kullanici Adi veya Sifre Yanlis <a href="/login">Geri</a> '+str(wrong))

	def set_current_user(self, user):
		if user:
			self.set_secure_cookie("user", tornado.escape.json_encode(user))
		else:
			self.clear_cookie("user")
     
class AuthLogoutHandler(tornado.web.RequestHandler):
	def get(self):
		logging.info("[LOGOUT] clearing cookie")
		self.clear_cookie("user")
		self.redirect(self.get_argument("next", "/"))
		
class EventsSocketHandler(tornado.websocket.WebSocketHandler):
	waiters = set()
	fullwaiters = set()
	
	cache = []
	cache_size = 500
	IDcache = {}
	IDcache_size =200
	
	def updateUsers(self, conx):
		totalWaiters=len(EventsSocketHandler.waiters)+len(EventsSocketHandler.fullwaiters)
		e={
			"option": "users",
			"body": "%d online users" % totalWaiters,
			"remote_ip": self.request.remote_ip,
			"action": conx
		}
		for w in EventsSocketHandler.waiters:
			w.write_message(e)
		for w in EventsSocketHandler.fullwaiters:
			w.write_message(e)
	
	def open(self):
		if self.request.uri.find('full')>0:
			EventsSocketHandler.fullwaiters.add(self)
		else:
			EventsSocketHandler.waiters.add(self)
			sendEvents(self)
		logMessage = "Connected user from %s. Total Users: %d" % (self.request.remote_ip, len(EventsSocketHandler.waiters))
		logging.info(logMessage)
		logging.info("[User-Agent]: %s", self.request.headers['User-Agent'])
		logging.info("[Origin]: %s", self.request.headers['Origin'])
		logging.info("[uri]: %s", self.request.uri)
		EventsSocketHandler.updateUsers(self, 'Connected')
		#self.test()
	def on_close(self):
		logging.info("User Disconnected")
		if self in EventsSocketHandler.waiters:
			EventsSocketHandler.waiters.remove(self)
		elif self in EventsSocketHandler.fullwaiters:
			EventsSocketHandler.fullwaiters.remove(self)
		EventsSocketHandler.updateUsers(self, 'Disconected')
	
	def on_message(self, message):
		logging.info("got event %r", message)
		parsed = tornado.escape.json_decode(message)
		event = {
			"id": str(uuid.uuid4()),
			"body": parsed["body"],
			}
		event["html"] = tornado.escape.to_basestring(self.render_string("events.html", event=event))
	
	def test(self):
		self.write_message("scheduled!")
		
        #ChatSocketHandler.update_cache(chat)
        #ChatSocketHandler.send_updates(chat)

def test():
	logging.info("event fired")
	
def test2():
	logging.info("PCB: event fired: waiters %d", len(EventsSocketHandler.waiters))
	for w in EventsSocketHandler.waiters:
		print w
		w.write_message("PCB")

def mongoSave(e):
	if e["option"]=="message":
		prev=coll.find_one({'id': e['id']})
		if prev:
			e['_id']=prev['_id']
		mongo_id=coll.save(e)
		#mongo_id=coll.insert(e)
		logging.info("Document saved %s. Documents in BBDD: %d" % (mongo_id, coll.count()))
	elif e["option"]=="update":
		coll.update({'id': e['id']}, {"$set": {'status': e['status']}}, upsert=False)
		coll.update({'id': e['id']}, {"$set": {'user': e['user']}}, upsert=False)
		updated=coll.find_one({'id': e['id']})
		print updated['_id']
		logging.info("Document updated %s. Documents in BBDD: %d" % (updated['_id'], coll.count()))
		
def mongoReadFull(size):
	for e in coll.find({'status': 'Closed'}):
		print e['user']

	

def updateEvents():
	global lastID
	states=["success", "info", "warning", "danger"]
	logging.info("[Update events]")
	if  len(EventsSocketHandler.waiters) >=1:
		if lastID==0:
			cursor.execute("select top 10 SM_SC_MESSAGE_ID,SM_MESSAGE_INSERTION_DATE_TIME,SM_MESSAGE_TEXT,SM_CRITICALNESS from %s.dbo.SCMSG_MESSAGE order by SM_SC_MESSAGE_ID desc" % database)
		else:
			cursor.execute("select SM_SC_MESSAGE_ID,SM_MESSAGE_INSERTION_DATE_TIME,SM_MESSAGE_TEXT,SM_CRITICALNESS from %s.dbo.SCMSG_MESSAGE where SM_SC_MESSAGE_ID>%d  order by SM_SC_MESSAGE_ID desc" % (database,lastID))
		rows=cursor.fetchall()
		logging.info("query executed: %d rows", len(rows))
		if len(rows)>0:
			logging.info("first row id: %d", rows[0][0])
			for row in reversed(rows):
				logging.info('[Event ID] %d', row[0])
				#logging.info(row[3])				
				#logging.info("last ID: %d",lastID)
				d=getDomain(row[0])
				s=getStatus(row[0])
				EventsSocketHandler.IDcache[str(row[0])]=s
				e=writeMessage(row, d,s)
				for w in EventsSocketHandler.waiters:
					e["html"] = tornado.escape.to_basestring(w.render_string("events.html", event=e))
					w.write_message(e)	
				mongoSave(e)
				#d=e
				#d["body"]=d["body"].replace('[','').replace(']','').replace(':','')
				#d.pop("body")
				#d.pop("url")
				#print d
				
			lastID=int(rows[0][0])
			logging.info("last ID: %d",lastID)
	checkUpdatedEvents()
	totalWaiters=len(EventsSocketHandler.waiters)+len(EventsSocketHandler.fullwaiters)
	logging.info("%d Connected users" % totalWaiters)
	#print EventsSocketHandler.IDcache

def clearCache():
	if len(EventsSocketHandler.IDcache)>EventsSocketHandler.IDcache_size:
		todelete=EventsSocketHandler.IDcache.keys()[EventsSocketHandler.IDcache_size:]
		for e in todelete:
			EventsSocketHandler.IDcache.pop(e)
		logging.info("[IDcache]: %d items - Deleted %d" %  (len(EventsSocketHandler.IDcache),len(todelete)))

def checkUpdatedEvents():
	todelete=[]
	logging.info("[Update status]")
	for eventID,s in EventsSocketHandler.IDcache.iteritems():
		ns=getStatus(int(eventID))
		if (s[0]!=ns[0]) or (s[1]!=ns[1]):
			EventsSocketHandler.IDcache[eventID]=ns
			logging.info("[Status Changed] Event: %s Status: %s User: %s" % (eventID,ns[0],ns[1]))
			e={
				"option": "update",
				"id": eventID,
				"status": ns[0],
				"user": ns[1],
			}
			if (ns[0]=='Closed'): 
				todelete.append(eventID)
			mongoSave(e)
			for w in EventsSocketHandler.waiters:
				w.write_message(e)
	for e in todelete:
		EventsSocketHandler.IDcache.pop(e)
	logging.info("[IDcache]: %d items - Deleted %d" %  (len(EventsSocketHandler.IDcache),len(todelete)))
	clearCache()

			
	

def sendEvents(w):
	logging.info("Sending events to waiter")
	global lastID
	startID=lastID-20
	
	if lastID==0:
		cursor.execute("select top 10 SM_SC_MESSAGE_ID,SM_MESSAGE_INSERTION_DATE_TIME,SM_MESSAGE_TEXT,SM_CRITICALNESS from %s.dbo.SCMSG_MESSAGE order by SM_SC_MESSAGE_ID desc" % database)
	else:
		cursor.execute("select SM_SC_MESSAGE_ID,SM_MESSAGE_INSERTION_DATE_TIME,SM_MESSAGE_TEXT,SM_CRITICALNESS from %s.dbo.SCMSG_MESSAGE where SM_SC_MESSAGE_ID>%d  order by SM_SC_MESSAGE_ID desc" % (database, startID))				
	rows=cursor.fetchall()
	if len(rows)>0:
		for row in reversed(rows):
			logging.info("[new waiter] "+str(row[0]))
			s=getStatus(row[0])
			EventsSocketHandler.IDcache[str(row[0])]=s
			e = writeMessage(row, getDomain(row[0]),s)
			e["html"] = tornado.escape.to_basestring(w.render_string("events.html", event=e))
			w.write_message(e)
			

def writeMessage(r,d,s):
	global states
	e = {
		"option": "message",
		"id": str(r[0]),
		"body": unicode(r[2], errors='ignore'),
		"criticalness": states[int(r[3])],
		"url": "",
		"domain": d,
		"dateTime": r[1],
		"status": s[0],
		"user": s[1],
		}
	
	#logging.info(e["body"])
	if e["body"].find('href')>0:
		e["body"]=e["body"].replace('#URL_NETFLOW#','').replace("href='0'",'')
		urls = re.findall('http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', e["body"])
		for url in urls:
			e["url"] = url[:url.find("'")]
		e["body"]=e["body"].replace(e["url"],'').replace("<a href=''>","").replace("</a>","").replace("\n","<br>")
		#logging.info("[Body] "+e["body"])
		#logging.info("[URL] "+e["url"])
	return e
	

def getDomain(eventid):
	cursor.execute("select SMD_DOMAIN_ID from %s.dbo.SCMSG_MESSAGE_DOMAIN where SMD_SC_MESSAGE_ID='%d'" % (database,eventid))
	domainid=cursor.fetchone()[0]
	cursor.execute("select  SD_DOMAIN_NAME from %s.dbo.SCMSG_DOMAIN where SD_DOMAIN_ID='%d'" % (database,domainid))
	domain_name=cursor.fetchone()[0]
	domainName=domain_name.split(' - ', 1)
	if len(domainName)>1:
		domain=domainName[1]
	else:
		domain=domainName[0]
	#logging.info("[Domain]: "+domain)
	return domain
	
def getAlldomains():
	cursor.execute("select SD_DOMAIN_NAME from %s.dbo.SCMSG_DOMAIN" % database)
	rows=cursor.fetchall()
	alldom=[]
	for row in rows:
		d=row[0].split(' - ', 1)
		if len(d)>1:
			alldom.append(d[1])
		else:
			alldom.append(d[0])
	return sorted(alldom)
		
	
def getStatus(eventid):
	st=["ACK", "Closed"]
	cursor.execute("select 	SMS_STATUS,SMS_USERNAME from %s.dbo.SCMSG_MESSAGE_STATUS where SMS_SC_MESSAGE_ID='%d'" % (database, eventid))
	status=cursor.fetchall()
	if len(status)==0:
		return ('Open','')
	else:
		for row in status:
			sms_status=row[0]
			sms_user=row[1]
		return (st[int(sms_status)-1],sms_user)

def main():
    tornado.options.parse_command_line()
    app = Application()
    app.listen(options.port)
    main_loop= tornado.ioloop.IOLoop.instance()
    #tornado.ioloop.PeriodicCallback(test2, 5000).start()
    tornado.ioloop.PeriodicCallback(updateEvents, PERIOD).start()
    #main_loop.add_timeout(datetime.timedelta(seconds=5), test)
    #remove in prod
    autoreload.start(main_loop)
    dirstowatch=['/vagrant/smartevents/static','/vagrant/smartevents/templates']
    for directory in dirstowatch:
		for dir, _, files in os.walk(directory):
			[autoreload.watch(dir + '/' +f) for f in files if not f.startswith('.')]
    main_loop.start()


if __name__ == "__main__":
	dsn = 'databasedatasource'
	user = 'DOMAIN\\user'
	password = 'password'
	database = 'database'
	PERIOD=30000
	
	con_string = 'DSN=%s;UID=%s;PWD=%s;DATABASE=%s;' % (dsn, user, password, database)
	cnxn = pyodbc.connect(con_string)
	cursor = cnxn.cursor()
	conn = Connection()
	db = conn.events
	coll = db.events
	
	lastID=0
	states=["success", "info", "warning", "danger"]
	domains=getAlldomains()
	#print domains
	#for d in domains:
	#	print d
	main()
