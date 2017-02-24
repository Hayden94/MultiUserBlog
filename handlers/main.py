import webapp2
import jinja2
import os
from models.post import Post
from models.comment import Comment
from models.user import User
from google.appengine.ext import db
from secure import make_secure_val, check_secure_val

template_dir = os.path.join('templates')
jinja_env = jinja2.Environment(
	loader=jinja2.FileSystemLoader(template_dir),
	autoescape=True
	)


def render_str(template, **params):
	t = jinja_env.get_template(template)
	return t.render(params)


def render_post(response, post):
	response.out.write('<b>' + post.subject + '</b><br>')
	response.out.write(post.content)


def blog_key(name='default'):
	return db.Key.from_path('blogs', name)


class Handler(webapp2.RequestHandler):
	def write(self, *a, **kw):
		self.response.out.write(*a, **kw)

	def render_str(self, template, **params):
		params['user'] = self.user
		return render_str(template, **params)

	def render(self, template, **kw):
		self.write(self.render_str(template, **kw))

	def set_secure_cookie(self, name, val):
		cookie_val = make_secure_val(val)
		self.response.headers.add_header(
			'Set-Cookie',
			'%s=%s; Path=/' % (name, cookie_val))

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

	# functions for post and comment validity
	def post_exists(self, post_id):
		post = Post.get_by_id(int(post_id), parent=blog_key())
		
		return post

	def comment_exists(self, post_id, comment_id):
		post = Post.get_by_id(int(post_id), parent=blog_key())
		comment = Comment.get_by_id(int(comment_id), parent=post)

		return post and comment

	# functions for users own post/comment validity
	def user_owns_post(self, post_id):
		post = Post.get_by_id(int(post_id), parent=blog_key())
		user_id = self.user.key().id()

		if user_id == post.creator:
			return post and user_id

	def user_owns_comment(self, post_id, comment_id):
		user_id = self.user.key()
		post = Post.get_by_id(int(post_id), parent=blog_key())
		comment = Comment.get_by_id(int(comment_id), parent=post)

		if user_id == comment.author.key():
			return post and comment

	# error page
	def render_error(self, post_id):
		post = Post.get_by_id(int(post_id), parent=blog_key())

		error = 'ERROR(404)'
		link_src = '/post/' + post_id
		link_name = 'Back'

		self.render(
			'information.html',
			error=error,
			link_src=link_src,
			link_name=link_name
			)


class Main(Handler):
	def get(self):
		posts = db.GqlQuery("select * from Post order by created desc limit 10")
		self.render(
			'front.html',
			posts=posts
			)
