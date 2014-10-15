import webapp2
import time
import os
from google.appengine.ext import ndb
import jinja2
import json
import hashlib

def hash_cookie(userid):
    return hashlib.sha256('userid').hexdigest()
def verify_cookie(hashed_cookie):
    if hash_cookie(json.load(open('users.json'))['username']) == hashed_cookie:
        return True
    else:
        return False

JINJA_ESSAY = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.dirname("templates/")),
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
    def nav(self,**args):
        nav ="<div id='nav'> ==NAV== </div>"
        sub =""
        for item in args[0]:
            if item(0) == '':
               sub+="<h1>%s%s</h1>"%item 
            else:
                sub+="<a herf = '%s'><h1>%s</h1></a>"%item
        nav.replace("==NAV==",sub)
        
        breadcrumbs="<div id='breadcrumbs'>==BREAD==</div>"
        sub=""
        for item in args[1]:
            sub+="<a herf='%s'>%s</a>"%item
        breadcrumbs.replace("==BREAD==",sub)
        return (nav,breadcrumbs)

class MainHandler(BasicHandler):
    def get(self):
        self.response.out.write('to be implemented')
        cookie=self.request.cookies.get('userid')
        self.response.out.write('<br/>%s'%cookie)
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
        self.render("EssayFront.html",essays=essays)
class LoginHandler(BasicHandler):
    def get(self):
        self.render("Login.html")
        
    def post(self):
        users=json.load(open("users.json"))
        username=self.request.get("username")
        password=self.request.get("password")
        error=None
        if username == "" or password =="":
            error= "all fields must be filled!"
        elif username==users["username"] and password==users["password"]:
            self.response.headers.add_header('Set-Cookie',
                                        'userid=%s' %hash_cookie(username))
            self.redirect("/essays/edit/")
        else:
            error= "username or password is incorrect"
        if error:
            self.render("Login.html",username=username,error=error)

class LogoutHandler(BasicHandler):
    def get(self):
        self.response.headers.add_header('Set-Cookie', 'userid=')
        self.redirect("/login")
             
class EditHandler(BasicHandler):
    def get(self,*args):
        cookie=self.request.cookies.get('userid')
        if not verify_cookie(cookie): 
            self.redirect("/login")
            return

        if args[0] == 'newpost':
            self.response.out.write("<h1>Newpost</h1>")
            self.render("EssayEdit.html", keyid=None)
        elif args[0] == '':
            self.render("Edit.html")
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
        cookie=self.request.cookies.get('userid')
        if not verify_cookie(cookie): 
            self.redirect("/login")
            return
        if title and body and url:

            if args[0] == 'newpost':
                post = ndb.gql("SELECT * FROM PostModel WHERE url=:url2",
                        url2=url).get().to_dict()
                if post == None:
                    new_post = PostModel(title =title, body=body,url=url)
                    new_post.put()
                elif post['url'] == url:
                    error="the url is already chosen please choose another one"
                else:
                    error = "something happend wrong"
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
    ('/essays', EssayList),
    ('/essays/([^/]+)', BlogHandler),
    ('/login',LoginHandler),
    ('/logout',LogoutHandler),
    webapp2.Route(r'/essays/edit/<:[^?/]*>', handler=EditHandler),
], debug=True)
