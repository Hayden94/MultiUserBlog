import os
import re
import random
import hashlib
import hmac
from string import letters

import webapp2
import jinja2

from google.appengine.ext import db

template_dir = os.path.join(os.path.dirname(__file__), 'templates')
jinja_env = jinja2.Environment(loader = jinja2.FileSystemLoader(template_dir),
							   autoescape = True)

SECRET = 'strike1298'

def render_str(template, **params):
	t = jinja_env.get_template(template)
	return t.render(params)

def make_secure_val(s):
	return "%s|%s" % (s, hmac.new(SECRET, s).hexdigest())

def check_secure_val(h):
	val = h.split('|')[0]
	if h == make_secure_val(val):
		return val

class BlogHandler(webapp2.RequestHandler):
	def write(self, *a, **kw):
		self.response.out.write(*a, **kw)

	def render_str(self, template, **params):
		params['user'] = self.user
		return render_str(template, **params)

	def render(self, template, **kw):
		self.write(self.render_str(template, **kw))

	def set_secure_cookie(self, name, val):
		cookie_val = make_secure_val(val)
		self.response.headers.add_header('Set-Cookie', '%s=%s; Path=/' % (name, cookie_val))

	def read_secure_cookie(self, name):
		cookie_val = self.request.cookies.get(name)
		return cookie_val and check_secure_val(cookie_val)

	def login(self, user):
		self.set_secure_cookie('user_id', str(user.key().id()))

	def logout(self):
		self.response.headers.add_header('Set-Cookie', 'user_id=; Path=/')

	def initialize(self, *s, **kw):
		webapp2.RequestHandler.initialize(self, *s, **kw)
		uid = self.read_secure_cookie('user_id')
		self.user = uid and User.by_id(int(uid))

def render_post(response, post):
	response.out.write('<b>' + post.subject + '</b><br>')
	response.out.write(post.content)

# user stuff
def make_salt(length = 5):
	return ''.join(random.choice(letters) for x in xrange(length))

def make_pw_hash(name, pw, salt = None):
	if not salt:
		salt = make_salt()
	h = hashlib.sha256(name + pw + salt).hexdigest()
	return '%s,%s' % (salt, h)

def valid_pw(name, password, h):
	salt = h.split(',')[0]
	return h == make_pw_hash(name, password, salt)

def users_key(group = 'default'):
	return db.Key.from_path('users', group)

class User(db.Model):
	name = db.StringProperty(required=True)
	pw_hash = db.StringProperty(required=True)
	email = db.StringProperty()

	@classmethod
	def by_id(cls, uid):
		return User.get_by_id(uid, parent = users_key())

	@classmethod
	def by_name(cls, name):
		u = User.all().filter('name =', name).get()
		return u

	@classmethod
	def register(cls, name, pw, email = None):
		pw_hash = make_pw_hash(name, pw)
		return User(parent = users_key(),
					name = name,
					pw_hash = pw_hash,
					email = email)

	@classmethod
	def login(cls, name, pw):
		u = cls.by_name(name)
		if u and valid_pw(name, pw, u.pw_hash):
			return u

##### blog stuff

def blog_key(name = 'default'):
	return db.Key.from_path('blogs', name)

# Post class for db

class Post(db.Model):
	subject = db.StringProperty(required = True)
	content = db.TextProperty(required = True)
	creator = db.IntegerProperty(required = True)
	created = db.DateTimeProperty(auto_now_add = True)
	last_modified = db.DateTimeProperty(auto_now = True)
	value = db.IntegerProperty(default = 0)

# Like model

class Likes(db.Model):
	user = db.IntegerProperty(required = True)
	haveliked = db.BooleanProperty(default = False)

# Comment model

class Comment(db.Model):
	author = db.ReferenceProperty(User, required=True)
	content = db.TextProperty(required=True)
	commentId = db.IntegerProperty(required=True)
	created = db.DateTimeProperty(auto_now_add = True)

#Blog Home

class BlogFront(BlogHandler):
	def get(self):
		posts = db.GqlQuery("select * from Post order by created desc limit 10")
		self.render('front.html', posts = posts)

# New post page

class NewPost(BlogHandler):
	def get(self):
		title = 'New Post'
		self.render("newpost.html", title = title)

	def post(self):
		if not self.user:
			return self.redirect('/login')

		subject = self.request.get('subject')
		content = self.request.get('content')
		creator = self.user.key().id()

		if subject and content:
			p = Post(parent = blog_key(), subject = subject, content = content, creator = creator)
			p.put()
			self.redirect('/post/%s' % str(p.key().id()))
		else:
			title = 'New Post'
			error = "Please enter both a subject and some content"

			self.render("newpost.html", title = title, subject=subject, content=content, error=error, edit = False)

# Post permalink

class PostPage(BlogHandler):
	def get(self, post_id):
		key = db.Key.from_path('Post', int(post_id), parent=blog_key())
		post = db.get(key)
		comments = Comment.all().ancestor(post)

		# make sure the post exists
		if not post:
			self.error(404)
			return
		# only logged in users may like posts
		if self.user:
			user_id = self.user.key().id()

			if Likes.all().ancestor(post).filter('user =', user_id).get():
				status = u"\U0001F44E"
			else:
				status = u"\U0001F44D"
			self.render('post.html', post = post, value = post.value, post_id = post_id, status = status,  comments = comments)
		else:
			status = u"\U0001F44D"
			self.render('post.html', post = post, value = post.value, post_id = post_id, status = status, comments = comments)

	def post(self, post_id):
		# only logged in users may like posts
		if not self.user:
			return self.redirect('/login')

		key = db.Key.from_path('Post', int(post_id), parent=blog_key())
		post = db.get(key)
		user_id = self.user.key().id()
		comments = Comment.all().ancestor(post)

		# users cannot like their own posts
		if user_id == post.creator:
			error = 'You cannot like your own posts'
			link_src = '/post/' + post_id
			link_name = 'Back'

			self.render('information.html', error = error, link_src = link_src, link_name = link_name)
		# like post and put into db
		else:
			l = Likes.all().ancestor(post).filter('user =', user_id).get()
			if l:
				l.delete()

				post.value -= 1
				post.put()
			else:
				like = Likes(parent = post, user = user_id, haveliked = True)
				like.put()

				if like.haveliked is True:
					post.value += 1

				post.put()

			self.redirect('/post/%s' % post_id)

# Edit Post Page

class EditPost(BlogHandler):
	def get(self, post_id):
		key = db.Key.from_path('Post', int(post_id), parent=blog_key())
		post = db.get(key)
		comments = Comment.all().ancestor(post)	
		title = 'Edit Post'

		if not self.user:
			self.redirect('/login')
		elif not self.user.key().id() == post.creator:
			error = 'You cannot edit another user\'s post'
			link_src = '/post/' + post_id
			link_name = 'Back'

			self.render('information.html', error = error, link_src = link_src, link_name = link_name)
		else:
			subject = post.subject
			content = post.content
			self.render("newpost.html", subject = subject, content = content, post_id = post_id, title = title, edit = True)

	def post(self, post_id):
		key = db.Key.from_path('Post', int(post_id), parent=blog_key())
		post = db.get(key)

		if (not self.user) or (not self.user.key().id() == post.creator):
			return self.redirect('/login')

		subject = self.request.get('subject')
		content = self.request.get('content')

		if subject and content:
			key = db.Key.from_path('Post', int(post_id), parent=blog_key())
			p = db.get(key)
			p.subject = subject
			p.content = content
			p.put()
			self.redirect('/post/%s' % post_id)
		else:
			title = 'Edit Post'
			error = 'Please enter both a subject and some content!'

			self.render('newpost.html', subject = subject, title = title, content = content, error = error, post_id = post_id, edit = True)

# Delete Post

class DeletePost(BlogHandler):
	def get(self, post_id):
		key = db.Key.from_path('Post', int(post_id), parent=blog_key())
		post = db.get(key)
		comments = Comment.all().ancestor(post)

		# only logged in users can delete posts
		if not self.user:
			self.redirect('/login')
		elif not self.user.key().id() == post.creator:
			error = 'You cannot delete another user\'s post'
			link_src = '/post/' + post_id
			link_name = 'Back'

			self.render('information.html', error = error, link_src = link_src, link_name = link_name)
		else:
			title = 'Post'
			message = 'Are you sure you want to delete this post?'

			self.render('delete.html', post = post, post_id = post_id, title = title, message = message, subject = post.subject, content = post.content)

	def post(self, post_id):
		key = db.Key.from_path('Post', int(post_id), parent=blog_key())
		post = db.get(key)

		if (not self.user) or (not self.user.key().id() == post.creator):
			return self.redirect('/login')
		else:
			post.delete()
			message = 'Your post has been deleted'
			link_src = '/'
			link_name = 'Home'

			self.render('information.html', message = message, link_src = link_src, link_name = link_name)

class AddComment(BlogHandler):
	def get(self, post_id):
		# only logged in users can add comments
		if not self.user:
			self.redirect('/login')
		else:
			self.render('comment.html', post_id = post_id)

	def post(self, post_id):
		# only logged in users can add comments
		if not self.user:
			self.redirect('/login')

		content = self.request.get('content')
		key = db.Key.from_path('Post', int(post_id), parent=blog_key())
		post = db.get(key)

		if content:
			comment = Comment(
				parent = post,
				content = content,
				author = self.user,
				commentId = int(post_id)
				)

			comment.put()
			self.redirect('/post/%s' % post_id)
		else:
			error = 'Please enter some content'

			self.render('comment.html', content = content, error = error)

# class DeleteComment(BlogHandler):
	# def get(self, post_id):
		# key = db.Key.from_path('Comment', int(post_id), parent = blog_key())
		# comment = db.get(key)

		# if not self.user:
			# self.redirect('/login')
		# elif not self.user.key() == comment.author.key():
			# self.write('<div style="text-align: center;">You are not allowed to delete this comment.<br><br>' +
						# '<a href="/">Home</a></div>')
		# else:
			# title = 'Comment'
			# message = 'Are you sure you want to delete this comment?'
			# content = comment.content
			# self.render('delete.html', title = title, message = message, content = content)    
	# def post(self):

# class EditComment(BlogHandler):
	# def get(self, post_id):
		# key = db.Key.from_path('Comment',int(post_id),parent=blog_key())
		# comment = db.get(key)

		# if not self.user:
			# self.redirect('/login')
		# elif not self.user.key() == comment.author.key():
			# self.write('You are not allowed to edit this comment')
		# else:
			# content = comment.content
			# self.render('comment.html', content = content, post_id = post_id, edit = True)

# Handler for welcome after sign up, deletion confirmation, etc.

class Information(BlogHandler):
	def get(self):
		if not self.user:
			self.redirect('/login')
		else:
			error = 'You have reached this page at an error'
			link_src = '/'
			link_name = 'Home'

			self.render('information.html', error = error, link_src = link_src, link_name = link_name)

#check valid signup inputs

USER_RE = re.compile(r"^[a-zA-Z0-9_-]{3,20}$")
def valid_username(username):
	return username and USER_RE.match(username)

PASS_RE = re.compile(r"^.{3,20}$")
def valid_password(password):
	return password and PASS_RE.match(password)

EMAIL_RE  = re.compile(r'^[\S]+@[\S]+\.[\S]+$')
def valid_email(email):
	return not email or EMAIL_RE.match(email)

#Signup Page

class Signup(BlogHandler):

	def get(self):
		self.render("signup.html")

	def post(self):
		have_error = False
		self.username = self.request.get('username')
		self.password = self.request.get('password')
		self.verify = self.request.get('verify')
		self.email = self.request.get('email')

		params = dict(username = self.username,
					  email = self.email)

		if not valid_username(self.username):
			params['error_username'] = "That's not a valid username."
			have_error = True

		if not valid_password(self.password):
			params['error_password'] = "That wasn't a valid password."
			have_error = True
		elif self.password != self.verify:
			params['error_verify'] = "Your passwords didn't match."
			have_error = True

		if not valid_email(self.email):
			params['error_email'] = "That's not a valid email."
			have_error = True

		if have_error:
			self.render('signup.html', **params)
		else:
			self.done()

	def done(self, *a, **kw):
		raise NotImplementedError

class Register(Signup):
	def done(self):
		#make sure the user doesn't already exist
		u = User.by_name(self.username)
		if u:
			msg = 'That user already exists.'
			self.render('signup.html', error_username = msg)
		else:
			u = User.register(self.username, self.password, self.email)
			u.put()

			self.login(u)

			message = 'Welcome, ' + self.username
			link_src = '/new'
			link_name = 'New Post'

			self.render('information.html', message = message, link_src = link_src, link_name = link_name)

class Login(BlogHandler):
	def get(self):
		self.render('login.html')
	
	def post(self):
		username = self.request.get('username')
		password = self.request.get('password')

		u = User.login(username, password)
		if u:
			self.login(u)
			self.redirect('/')
		else:
			msg = 'Invalid Login'
			self.render('login.html', error = msg)

class Logout(BlogHandler):
	def get(self):
		self.logout()
		self.redirect('/')

app = webapp2.WSGIApplication([('/', BlogFront),
							   ('/new', NewPost),
							   ('/signup', Register),
							   ('/login', Login),
							   ('/logout', Logout),
							   ('/post/([0-9]+)', PostPage),
							   ('/edit/([0-9]+)', EditPost),
							   ('/delete/([0-9]+)', DeletePost),
							   ('/comment/([0-9]+)', AddComment),
							   # ('/comment/edit/([0-9]+)', EditComment)
							   # ('/comment/([0-9]+)/delete/([0-9]+)', DeleteComment).
							   ('/info', Information)
							   ],
							  debug=True)
