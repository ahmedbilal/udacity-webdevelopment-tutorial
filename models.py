from google.appengine.ext import ndb

# Model
class BlogPost(ndb.Model):
    subject = ndb.StringProperty(indexed=True)
    body = ndb.TextProperty()
    publish_date = ndb.DateTimeProperty(auto_now_add=True)


class User(ndb.Model):
    username = ndb.StringProperty(indexed=True)
    password = ndb.StringProperty()
    email = ndb.StringProperty()