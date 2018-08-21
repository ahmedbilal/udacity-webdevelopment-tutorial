from peewee import *
import datetime


# Setting up PeeWee with Postgres
db = PostgresqlDatabase('postgres', user='postgres', password='',
                        host='localhost', port=5432)

db.connect()

# Model
class BlogPost(Model):
    subject = CharField()
    body = TextField()
    publish_date = DateTimeField(default=datetime.datetime.now())

    class Meta:
        database = db

class User(Model):
    username = CharField()
    password = CharField()
    email = CharField()

    class Meta:
        database = db


# db.drop_tables([BlogPost])
db.create_tables([BlogPost, User])
