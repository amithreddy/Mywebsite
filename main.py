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
        essays = ndb.gql("SELECT * FROM PostModel").fetch(10)
        essays = [essay.to_dict() for essay in essays]
        print essays[0]
        self.render("EssayFront.html",essays=essays)

class EditHandler(BasicHandler):
    def get(self,*args):
        if args[0] == 'newpost':
            self.response.out.write("<h1>Newpost</h1>")
            self.render("EssayEdit.html", keyid=None)
        else:
            q= ndb.gql("SELECT * FROM PostModel WHERE url=:url2",
            url2=args[0])
            
            if q.get() !=None:
                post= q.get().to_dict()
                keyid= q.get().key.id()
                self.response.out.write("<h1>Editing %s</h1>"%post['title'])
                self.render("EssayEdit.html",date=post['date'],
                            url=post['url'],keyid=keyid,
                            body=post['body'],title= post['title'])
                            
            else:
                self.response.out.write("the essay %s doesn't exist" %args[0])
    def post(self,*args):
        keyid= self.request.get('keyid')
        title =self.request.get('title')
        url = self.request.get('url')
        body = self.request.get('body')
        error= False
        if title and body and url:
            if args[0] == 'newpost':
                post = ndb.gql("SELECT * FROM PostModel WHERE url=:url2",
                        url2=url).get()
                if post['url'] == url:
                    error="the url is already chosen please choose another one"
                else:
                    new_post = PostModel(title =title, body=body,url=url)
                    new_post.put()
            elif keyid != None:
                update = PostModel.get_by_id(int(keyid))
                dburl = ndb.gql("SELECT * FROM PostModel WHERE url=:url2",
                        url2=url).get()
                if dburl ==None: 
                    update.title=title
                    update.url=url
                    update.body=body
                    update.put()
                elif dburl.url == update.url:
                    update.title=title
                    update.url=url
                    update.body=body
                    update.put()
                else:
                    error= "the url is already chosen please chose another one"
            else:
                error= "something unexpected happend call the dev"
        else:
            error="all text must be filled"

        if error:
            self.render("EssayEdit.html",title=title,
            body=body,url=url,error=error,keyid=keyid)
        else:
            time.sleep(0.1)
            self.redirect('/essays/%s'%url)
                   
app = webapp2.WSGIApplication([
    ('/', MainHandler),
    ('/essays/', EssayList),
    ('/essays/([^/]+)', BlogHandler),
    webapp2.Route(r'/essays/edit/<:[^?/]*>', handler=EditHandler),
], debug=True)
