from main import Handler, blog_key
from models.post import Post

class EditPost(Handler):
	def get(self, post_id):
		post = Post.get_by_id(int(post_id), parent = blog_key())
		title = 'Edit Post'

		# if post doesn't exist
		if not self.post_exists(post_id):
			self.render_error(post_id)
		# only logged in users can delete posts
		elif not self.user:
			self.redirect('/login')
		elif not self.user_owns_post(post_id):
			error = 'You cannot edit another user\'s post'
			link_src = '/post/' + post_id
			link_name = 'Back'

			self.render('information.html', error = error, link_src = link_src, link_name = link_name)
		# if the user is not the author of the post
		else:
			subject = post.subject
			content = post.content
			self.render("newpost.html", subject = subject, content = content, post_id = post_id, title = title, edit = True)

	def post(self, post_id):
		post = Post.get_by_id(int(post_id), parent = blog_key())
		subject = self.request.get('subject')
		content = self.request.get('content')

		# if post doesn't exist
		if not self.post_exists(post_id):
			self.render_error(post_id)
		# only logged in users can delete posts
		elif not self.user:
			self.redirect('/login')
		# if subject and content section has values
		elif (subject and content) and self.user_owns_post(post_id):
			p = Post.get_by_id(int(post_id), parent = blog_key())
			p.subject = subject
			p.content = content
			p.put()
			self.redirect('/post/%s' % post_id)
		# if either subject or content don't have values
		elif not (subject and content):
			title = 'Edit Post'
			error = 'Please enter both a subject and some content!'

			self.render('newpost.html', subject = subject, title = title, content = content, error = error, post_id = post_id, edit = True)