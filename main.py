import webapp2
from google.appengine.ext import ndb

class MainHandler(webapp2.RequestHandler):
    def get(self):
        self.response.write('Hello world!')

class BlogHandler(webapp2.RequestHandler):
    def get(self,essay_id):
        pass

class EditHandler(webapp2.RequestHandler):        

app = webapp2.WSGIApplication([
    ('/', MainHandler),
    ('/essay/<essay_id>',BlogHandler),
    ('/edit',EditHandler),
], debug=True)
