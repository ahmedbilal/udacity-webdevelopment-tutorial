import webapp2
import cgi
import re
import jinja2
from os.path import join, dirname

template_dir = join(dirname(__file__), "templates")
jinja_env = jinja2.Environment(loader=jinja2.FileSystemLoader(template_dir))

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

class SignupApp(webapp2.RequestHandler):
    page = """
                <doctype html>
                <html>
                    <head>
                        <title>Signup</title>

                    </head>
                    <body>
                    {body}
                    </body>
                </html>    
            """
    form = """  
                <h1>Signup</h1>
                <form method="post">
                    <label for="username">Username</label>
                    <input type="text" id="username" name="username" value="{username}" />
                    <span class="error" id="username_error" style="color:red">{username_error}</span>
                    <br/>

                    <label for="password">Password</label>
                    <input type="password" id="password" name="password" />
                    <span class="error" id="password_error" style="color:red">{password_error}</span>
                    <br/>

                    <label for="verify">Verify Password</label>
                    <input type="password" id="verify" name="verify" />
                    <span class="error" id="verify_error" style="color:red">{verify_error}</span>
                    <br/>

                    <label for="email">Email</label>
                    <input type="email" id="email" name="email" value="{email}" />
                    <span class="error" id="email_error" style="color:red">{email_error}</span>
                    <br/>

                    <input type="submit" />
                </form>
    """

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

        self.response.write(self.page.format(body = self.form).format(username_error=username_error, password_error=password_error,
                                             verify_error=verify_error, email_error=email_error, username="", email=""))

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
        if not self.is_email_valid(email):
            email_error = "Invalid Email"

        if not username_error and not password_error and not verify_error and not email_error:
            return webapp2.redirect('/welcome?username={}'.format(username))
        
        self.response.write(self.form.format(username_error=username_error, password_error=password_error,
                                             verify_error=verify_error, email_error=email_error,
                                             username=username, email=email))

class WelcomeApp(webapp2.RequestHandler):
    output = """
            <h1>Welcome {username}</h1>
            """

    def get(self):
        username = self.request.get("username")
        self.response.write(self.output.format(username=username))

class HelloApp(webapp2.RequestHandler):
    def write(self, *args, **kwargs):
        self.respone.write(*args, **kwargs)

    def render_str(self, template, **args):
        t = jinja2_env.get_template(template)
        return t.render(args)

    def render(self, template, **kw):
        self.write(self.render_str(template, **kw))
    
app = webapp2.WSGIApplication([
    ('/', Rot13App),
    ('/signup', SignupApp),
    ('/welcome', WelcomeApp)
], debug=True)


def main():
    from paste import httpserver
    httpserver.serve(app, host='127.0.0.1', port='8000')


if __name__ == '__main__':
    main()