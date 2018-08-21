import cgi
import re
import datetime
import hmac
from os.path import join, dirname
from models import BlogPost, User
import webapp2
import jinja2
from utility import make_secure_val, init_hmac, ret_secure_val
from peewee import DoesNotExist
import json

# Setting up Jinja2
template_dir = join(dirname(__file__), "templates")
jinja2_env = jinja2.Environment(loader=jinja2.FileSystemLoader(template_dir), autoescape=True)


class Handler(webapp2.RequestHandler):
    def write(self, *args, **kwargs):
        self.response.write(*args, **kwargs)

    def render_str(self, template, **args):
        t = jinja2_env.get_template(template)
        return t.render(args)

    def render(self, template, **kw):
        self.write(self.render_str(template, **kw))

class Rot13App(webapp2.RequestHandler):
    form = """
        <form method="post">
            <h1>ROT13</h1>
            <textarea name="text" rows="4" cols="50">{content}</textarea>
            <br/>
            <input type="submit" />
        </form>
        """
    def rot(self, string, n):
        rotated_string = ""
        for char in string:
            first_char = ''
            last_char = ''

            if char.isupper():
                first_char = 'A'
                last_char = 'Z'
            elif char.islower():
                first_char = 'a'
                last_char = 'z'
            if char.isalpha():
                if ((ord(char) + n) / float(ord(last_char))) > 1:
                    rotated_string = rotated_string + chr(ord(first_char) + (ord(char) + n - 1) % ord(last_char))
                else:
                    rotated_string = rotated_string + chr(ord(char) + n)
            else:
                rotated_string = rotated_string + char
        return cgi.escape(rotated_string)

    def get(self):
        self.response.write(self.form.format(content=""))
    
    def post(self):
        text = self.request.get("text")
        self.response.write(self.form.format(content=self.rot(text, 13)))

class LoginApp(Handler):
    def get(self):
        username_error = ""
        password_error = ""
        username = ""
        password = ""
        self.render("login.html", username = username, password = password, 
                    username_error=username_error, password_error=password_error)

    def post(self):
        username_error = ""
        password_error = ""
        username = self.request.get("username")
        password = self.request.get("password")

        if not username:
            username_error = "Please enter your username"
        
        if not password:
            password_error = "Please enter password"

        # if both username is filled and password is filled then go down this road
        if username and password:
            try:
                user = User.get(User.username == username)
                if user.password != password:
                    password_error = "password is wrong."
            except DoesNotExist:
                username_error = "{username} does not exists".format(username=username)
            
            if not username_error and not password_error:
                self.response.headers.add_header("Set-Cookie", "user={}; Domain=127.0.0.1; Path=/; Max-Age=1200".\
                                      format(make_secure_val(str(user.id))))
                webapp2.redirect('/welcome', response=self.response)
        
        self.render("login.html", username = username, password = password, 
                username_error=username_error, password_error=password_error)


class SignupApp(Handler):
    def is_username_valid(self, username):
        USER_RE = re.compile(r"^[a-zA-Z0-9_-]{3,20}$")
        return USER_RE.match(username)
    
    def is_password_valid(self, password):
        PSWD_RE = re.compile(r"^.{3,20}$")
        return PSWD_RE.match(password)

    def is_email_valid(self, email):
        EMAIL_RE = re.compile(r"^[\S]+@[\S]+.[\S]+$")
        return EMAIL_RE.match(email)

    def get(self):
        username_error = ""
        password_error = ""
        verify_error = ""
        email_error = ""
        self.render("signup.html", username_error=username_error, password_error=password_error,
                    verify_error=verify_error, email_error=email_error, username="", email="")

    def post(self):
        username = self.request.get("username")
        password = self.request.get("password")
        verify = self.request.get("verify")
        email = self.request.get("email")
        
        username_error = ""
        password_error = ""
        verify_error = ""
        email_error = ""

        if not self.is_username_valid(username):
            username_error = "Invalid Username"
        if not self.is_password_valid(password):
            password_error = "Invalid Password"
        if password != verify:
            verify_error = "Password and Verify password must be same"
        if email and not self.is_email_valid(email):
            email_error = "Invalid Email"
        try:
            user = User.get(User.username == username)
            username_error = "User with '" + user.username + "' exists"
        except DoesNotExist:
            if not username_error and not password_error and not verify_error and not email_error:
                user = User.create(username=username, password=password, email=email)
                user.save()

                self.response.headers.add_header("Set-Cookie", "user={}; Domain=127.0.0.1; Path=/; Max-Age=60".\
                                      format(make_secure_val(str(user.id))))
                # self.response.set_cookie('user', str(user.id), path='/', domain="127.0.0.1")
                webapp2.redirect('/welcome', response=self.response)
        
        self.render("signup.html", username_error=username_error, password_error=password_error,
                                             verify_error=verify_error, email_error=email_error,
                                             username=username, email=email)


class LogoutApp(Handler):
    def get(self):
        user_id = self.request.cookies.get('user')
        if user_id:
            user_id = ret_secure_val(user_id)
        else:
            return webapp2.redirect('/signup')

        self.response.headers.add_header("Set-Cookie", "user={}; Domain=127.0.0.1; Path=/; Max-Age=-60".\
                                      format(make_secure_val(str(user_id))))
        return webapp2.redirect('/signup')

class WelcomeApp(webapp2.RequestHandler):
    output = """
            <h1>Welcome {username}</h1>
            """

    def get(self):
        user_id = self.request.cookies.get('user')
        if user_id:
            user_id = ret_secure_val(user_id)
        if user_id is None:
            return webapp2.redirect('/signup')
        username = User.get_by_id(user_id).username
        self.response.write(self.output.format(username=username))

class BlogPostList(Handler):
    def get(self):
        self.render("blog.html", blog_post=BlogPost.select())

class BlogPostDetail(Handler):
    def get(self, blogpost_id):
        self.render("post.html", post=BlogPost.get_by_id(blogpost_id))

class NewPostApp(Handler):
    def get(self):
        self.render("new_post.html")

    def post(self):
        subject = self.request.get("subject").strip()
        content = self.request.get("content").strip()
        error = ""
        if not subject and not content:
            error = "Please fill both subject and content"
        elif not subject:
            error = "Please fill subject"
        elif not content:
            error = "Please fill content"
        
        if error:
            self.render("new_post.html", error=error, subject=subject, content=content)
        else:
            p = BlogPost.create(subject=subject, body=content)
            p.save()
            self.redirect("/blog/" + str(p.id))

class BlogPostDetailJson(Handler):
    def get(self, blogpost_id):
        self.response.headers['Content-Type'] = 'application/json'
        post = BlogPost.get_by_id(blogpost_id)
        post_detail = {
                    "subject": post.subject,
                    "content": post.body,
                    "created": str(post.publish_date),
                }
        self.response.out.write(json.dumps(post_detail))


class BlogPostListJson(Handler):
    def get(self):
        posts = BlogPost.select()
        self.response.headers['Content-Type'] = 'application/json'
        result = []
        for post in posts:
            _id = post.id
            subject = post.subject
            body = post.body
            publish_date = post.publish_date
            result.append({
                    "subject": subject,
                    "content": body,
                    "created": str(publish_date),
                })
        self.response.out.write(json.dumps(result))
        # return json.dumps()

app = webapp2.WSGIApplication([
    ('/', Rot13App),
    ('/signup', SignupApp),
    ('/login', LoginApp),
    ('/logout', LogoutApp),
    ('/welcome', WelcomeApp),
    ('/blog', BlogPostList),
    ('/blog.json', BlogPostListJson),
    (r'/blog/(\d+)', BlogPostDetail),
    (r'/blog/(\d+).json', BlogPostDetailJson),
    ('/blog/newpost', NewPostApp)
], debug=True)


def main():
    from paste import httpserver
    httpserver.serve(app, host='127.0.0.1', port='8090')


if __name__ == '__main__':
    main()