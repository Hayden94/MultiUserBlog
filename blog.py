import os

import webapp2
import jinja2
import string

from google.appengine.ext import db
import secure
from handlers import *

app = webapp2.WSGIApplication([
	('/', Main),
	('/new', NewPost),
	('/signup', Register),
	('/login', Login),
	('/logout', Logout),
	('/post/([0-9]+)', PostPage),
	('/like/([0-9]+)', LikePost),
	('/edit/([0-9]+)', EditPost),
	('/delete/([0-9]+)', DeletePost),
	('/comment/([0-9]+)', AddComment),
	('/comment/edit/([0-9]+)/([0-9]+)', EditComment),
	('/comment/delete/([0-9]+)/([0-9]+)', DeleteComment),
	('/info', Information)],
	debug=True)
