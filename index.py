import wsgiref.handlers
from google.appengine.ext import webapp
import logging
from google.appengine.ext.webapp import template
import os
from util.sessions import Session
import urllib2
import random
from django.utils import simplejson as json

country_url = 'https://restcountries.eu/rest/v1/all'
country_data = json.load(urllib2.urlopen(country_url))

def doRender(handler, tname='index.html', values={}):
	temp = os.path.join(os.path.dirname(__file__), 'templates/' + tname)
	if not os.path.isfile(temp):
		return False

	newval = dict(values)
	newval['path'] = handler.request.path
	handler.session = Session()
	if 'country' in handler.session:
		newval['country'] = handler.session['country']
	outstr = template.render(temp, newval)
	handler.response.out.write(unicode(outstr))
	return True

class CountryHandler(webapp.RequestHandler):

	def post(self):
		self.session = Session()
		country_number = random.randint(0,247)
		mycountry = country_data[country_number]['name']
		self.session['country'] = mycountry
		doRender(self, 'country.html', {'country': mycountry})

class CapitalHandler(webapp.RequestHandler):

	def get(self): 
		self.session = Session()
		self.session.delete_item('username')
		doRender(self,'index.html')

	def post(self):
		self.session = Session()
		guess_capital = str(self.request.get('capital'))
		for country in country_data:
			if country['name']==self.session['country']:
				self.session['capital'] = country['capital']
		true_capital = self.session['capital']
		if guess_capital != true_capital:
			doRender(self, 'country.html', {'error': 'Guess again...'})
		else:
			doRender(self,'capital.html', {'capital': true_capital})

class MainHandler(webapp.RequestHandler):
	def get(self):
			path = self.request.path
			if doRender(self,path):
				return
			doRender(self,'index.html')

	def post(self):
			path = self.request.path
			temp = os.path.join(os.path.dirname(__file__), 'templates' + path)
			if not os.path.isfile(temp):
				temp = os.path.join(os.path.dirname(__file__), 'templates/index.html')
			outstr = template.render(temp, { })
			self.response.out.write(unicode(outstr))

def main():
	application = webapp.WSGIApplication([
		('/country', CountryHandler),
		('/capital', CapitalHandler),
		('/.*',MainHandler)],
		debug=True)
	wsgiref.handlers.CGIHandler().run(application)

if __name__=='__main__':
	main()