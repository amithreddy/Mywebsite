import webapp2
import os
from google.appengine.ext import ndb
import jinja2

JINJA_ESSAY = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.dirname("templates/essay/")),
    extensions = ['jinja2.ext.autoescape'],
    autoescape=True)
JINJA_MAIN = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.dirname("/templates/essay")),
    extensions = ['jinja2.ext.autoescape'],
    autoescape=True)
    
class PostModel(ndb.Model):
    date = ndb.DateProperty(auto_now_add=True)
    title = ndb.StringProperty()
    body = ndb.TextProperty()
    url = ndb.StringProperty()
    
class MainHandler(webapp2.RequestHandler):
    def get(self):
        self.response.out.write('to be implemented')        
class testHandler(webapp2.RequestHandler):
    def get(self,*test):#, test_id):
        print test
        self.response.write("essay url = %s"% test)

class BlogHandler(webapp2.RequestHandler):
    def get(self,essay_id):
        q= ndb.gql("SELECT * FROM PostModel WHERE url=:url2",
        url2=essay_id).get()
        #template= JINJA_ESSAY.get_template("Essay.html")
        #self.response.out.write(template.render(q))

        self.response.write("essay url = %s"% essay_id)
class EssayList(webapp2.RequestHandler):
    def get(self):  
        essays = ndb.gql("SELECT * FROM PostModel").get(10)
        template= JINJA_ESSAY.get_template("EssayFront.html")
        self.response.out.write(template.render(
                                    [essay.to_dict() for essay in essays]))

def get_from_response(**argws):
    return [self.response.get(a) for a in argws]    

class EditHandler(webapp2.RequestHandler):
    def get(self):
        template = JINJA_ESSAY.get_template("EssayEdit.html")
        self.response.out.write(template.render())
    def post(self):
        title =self.request.POST.get('title')
        url = self.request.POST.get('url')
        body = self.request.POST.get('body')
        error= False
        if title and body and url:
            condition = ndb.gql("SELECT * FROM PostModel WHERE url=:url2",
                        url2=url).get()
            if condition == None:
                new_post = PostModel(title =title, body=body,url=url)
                new_post.put()
                self.redirect("/essays/%s"%url)
            else:
                error="the url is already chosen please choose another one"
        else:
            error="all text must be filled"

        if error:
            template = JINJA_ESSAY.get_template("EssayEdit.html")
            self.response.out.write(template.render(title=title,
            body=body,url=url,error=error))
                   
app = webapp2.WSGIApplication([
    ('/', MainHandler),
    #essay_id matches everything but a slash
    ('/essays/', EssayList),
    ('/essays/([^/]+)', BlogHandler),
    ('/edit', EditHandler),
], debug=True)
