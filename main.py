#!/usr/bin/env python

import webapp2
import urllib
import os
from urlparse import urlparse
import jinja2
import re
import json

template_dir = os.path.join(os.path.dirname(__file__))
jinja_env = jinja2.Environment(loader = jinja2.FileSystemLoader(template_dir), autoescape = True)
site_url = 'http://wpdownloadstats.appspot.com'

class Handler(webapp2.RequestHandler):
	def write(self,*a,**kw):
		self.response.out.write(*a,**kw)
	def render_str(self,template,**params):
		t = jinja_env.get_template(template)
		return t.render(params)
	def render(self, template, **kw):
		self.write(self.render_str(template, **kw))
	def getstats(self, slug, w): #w means which i.e either plugins or theme slug is passed
		try:
			if(w == "Theme"):
				visiturl = 'http://wordpress.org/themes/' + slug + '/stats'
				pattern = re.compile('<td>(.+?)</td>') #this is for theme
			elif(w == "Plugin"):
				visiturl = 'http://wordpress.org/plugins/' + slug + '/stats'
				pattern = re.compile('</th>.*\n.*\t<td>(.+?)</td>') #this is for plugins
				
			htmlfile = urllib.urlopen(visiturl).read()
			pattern2 = re.compile('<span>(.+?) out of 5 stars</span>') # this is for ratings and is common for both theme and plugins
			datafound = re.findall(pattern, htmlfile) + re.findall(pattern2, htmlfile)
			datafound = {'today': (int)(datafound[0].replace(',','')),
	                        'yesterday': (int)(datafound[1].replace(',','')),
	                        'lastweek': (int)(datafound[2].replace(',','')),
	                        'alltime': (int)(datafound[3].replace(',','')),
	                        'ratings': (float)(datafound[4].replace(',',''))
	                       }
			if(len(datafound) < 5):
				return 0
			else:
				return datafound
		except:
			return 0	
class MainHandler(Handler):
	def get(self):
		self.render("index.html",urlhome=site_url)
	def post(self):
		try:
			userSlug = self.request.get("slug") #get the plugin or theme name
			userChoice = self.request.get("themeorplugin") #get either theme or plugin from dropdown menu
			allstats = 0
			if userSlug:
				allstats = self.getstats(userSlug, userChoice)
				if (allstats):
					self.render("index.html",today=allstats['today'],
						yesterday=allstats['yesterday'],
						lastweek=allstats['lastweek'],
						alltime=allstats['alltime'],
						urlhome=site_url,
						ratings=allstats['ratings'])
				else:
					self.render("index.html",failed=1,urlhome=site_url,message="Please provide valid slug name for " + userChoice)
			else:
				self.render("index.html",failed=1,urlhome=site_url,message="Please do not submit blank!")
			#self.response.write("Choice = " + userChoice + ", allstats = " + str(allstats) + ", slug = " + str(userSlug))	
		except:
			self.render("index.html",failed=1,urlhome=site_url,message="Something went wrong seriously!")
				
class gettheme(Handler):
	def get(self,slug):
		self.response.headers['Content-Type'] = "application/json; charset=UTF-8"
		try:
			allstats = self.getstats(slug, "Theme")
			if(allstats !=0):
				jsonoutput = json.dumps(allstats)
				self.response.out.write(jsonoutput)
			else:
				self.response.out.write("Bad Request! i was supposed to get valid theme slug after /getinfo/t/")	
		except:
			self.response.out.write("Bad Request! i was supposed to get valid theme slug after /getinfo/t/")

class getplugins(Handler):
	def get(self,slug):
		self.response.headers['Content-Type'] = "application/json; charset=UTF-8"
		try:
			allstats = self.getstats(slug, "Plugin")
			if(allstats !=0):
				jsonoutput = json.dumps(allstats)
				self.response.out.write(jsonoutput)
			else:
				self.response.out.write("Bad Request! i was supposed to get valid plugins slug after /getinfo/p/")	
		except:
			self.response.out.write("Bad Request! i was supposed to get valid plugins slug after /getinfo/p/")

app = webapp2.WSGIApplication([('/', MainHandler),('/getinfo/t/(.+?)',gettheme),('/getinfo/p/(.+?)',getplugins)],debug=True)