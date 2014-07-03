import webapp2
from google.appengine.ext import ndb

class MainHandler(webapp2.RequestHandler):
    def get(self):
        self.response.write('Hello world!')

class BlogHandler(webapp2.RequestHandler):
    def get(self,essay_id):
        pass

class EditHandler(webapp2.RequestHandler): 
    def get(self):
        pass
    
    def post(self):
        pass

class BlogModel(ndb.Model):
    date = ndb.DateProtery(auto_now_add=True)
    title = ndb.StringProperty()
    body = ndb.TextProtery
    url = ndb.StringProtery()


              

app = webapp2.WSGIApplication([
    ('/', MainHandler),
    ('/essay/<essay_id>',BlogHandler),
    ('/edit',EditHandler),
], debug=True)
