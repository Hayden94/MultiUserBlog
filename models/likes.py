from google.appengine.ext import db

class Likes(db.Model):
	user = db.IntegerProperty(required = True)
	haveliked = db.BooleanProperty(default = False)