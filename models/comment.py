from google.appengine.ext import db
from user import User


class Comment(db.Model):
    author = db.ReferenceProperty(User, required=True)
    content = db.TextProperty(required=True)
    commentId = db.IntegerProperty(required=True)
    created = db.DateTimeProperty(auto_now_add=True)
