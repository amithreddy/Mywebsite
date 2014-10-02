import webapp2
import time
import os
from google.appengine.ext import ndb
import jinja2

JINJA_ESSAY = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.dirname("templates/essay/")),
    extensions = ['jinja2.ext.autoescape'],
    autoescape=True)
JINJA_MAIN = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.dirname("/templates")),
    extensions = ['jinja2.ext.autoescape'],
    autoescape=True)
    
class PostModel(ndb.Model):
    date = ndb.DateProperty(auto_now_add=True)
    title = ndb.StringProperty()
    body = ndb.TextProperty()
    url = ndb.StringProperty()

class BasicHandler(webapp2.RequestHandler):
    def render(self, template_name,**kwargs):
        template = JINJA_ESSAY.get_template(template_name)
        self.response.out.write(template.render(**kwargs))   

class MainHandler(BasicHandler):
    def get(self):
        self.response.out.write('to be implemented')
class BlogHandler(BasicHandler):
    def get(self,essay_id):
        q= ndb.gql("SELECT * FROM PostModel WHERE url=:url2",
            url2=essay_id).get()
        if q == None:
            self.response.write("essay does not exist")
        else:
            post= q.to_dict()
            self.render("Essay.html",date=post['date'],url=post['url'],
                            body=post['body'],title= post['title'])
class EssayList(BasicHandler):
    def get(self):
        essays = ndb.gql("SELECT * FROM PostModel").get(10)
        template= JINJA_ESSAY.get_template("EssayFront.html")
        self.response.out.write(template.render(
                                    [essay.to_dict() for essay in essays]))

class EditHandler(BasicHandler):
    def get(self):
        self.render("EssayEdit.html")
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
                time.sleep(1)
                self.redirect('/essays/%s'%url)
            else:
                error="the url is already chosen please choose another one"
        else:
            error="all text must be filled"

        if error:
            self.render("EssayEdit.html",title=title,
            body=body,url=url,error=error)
                   
app = webapp2.WSGIApplication([
    ('/', MainHandler),
    #essay_id matches everything but a slash
    ('/essays/', EssayList),
    ('/essays/([^/]+)', BlogHandler),
    ('/edit', EditHandler),
], debug=True)
