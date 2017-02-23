import re
from main import Handler
from models.user import User

# Check valid signup inputs

USER_RE = re.compile(r"^[a-zA-Z0-9_-]{3,20}$")
def valid_username(username):
	return username and USER_RE.match(username)

PASS_RE = re.compile(r"^.{3,20}$")
def valid_password(password):
	return password and PASS_RE.match(password)

EMAIL_RE  = re.compile(r'^[\S]+@[\S]+\.[\S]+$')
def valid_email(email):
	return not email or EMAIL_RE.match(email)

class Signup(Handler):

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
			params['error_username'] = "Please enter a valid username."
			have_error = True

		if not valid_password(self.password):
			params['error_password'] = "Please enter a valid password."
			have_error = True
		elif self.password != self.verify:
			params['error_verify'] = "Please enter matching passwords."
			have_error = True

		if not valid_email(self.email):
			params['error_email'] = "Please enter a valid email."
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