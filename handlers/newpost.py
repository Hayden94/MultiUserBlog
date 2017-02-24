from main import Handler
from models.user import User
from models.post import Post
from main import blog_key


class NewPost(Handler):
	def get(self):
		if self.user:
			title = 'New Post'
			self.render(
				"newpost.html", 
				title=title
				)
		else:
			self.redirect('/login')

	def post(self):
		if not self.user:
			return self.redirect('/login')

		subject = self.request.get('subject')
		content = self.request.get('content')
		creator = self.user.key().id()

		if subject and content:
			p = Post(
				parent=blog_key(),
				subject=subject,
				content=content,
				creator=creator
				)
			p.put()
			self.redirect('/post/%s' % str(p.key().id()))
		else:
			title = 'New Post'
			error = "Please enter both a subject and some content"

			self.render(
				"newpost.html",
				title=title,
				subject=subject,
				content=content,
				error=error,
				edit=False
				)
