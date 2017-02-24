from main import Handler, blog_key
from models.post import Post
from models.comment import Comment


class AddComment(Handler):
	def get(self, post_id):
		post = Post.get_by_id(int(post_id), parent=blog_key())

		# if post doesn't exist
		if not self.post_exists(post_id):
			self.render_error(post_id)
		# only logged in users can add comments
		elif not self.user:
			self.redirect('/login')
		else:
			title = 'Add Comment'

			self.render(
				'comment.html',
				title=title,
				post_id=post_id,
				addcomment=True
				)
	
	def post(self, post_id):
		post = Post.get_by_id(int(post_id), parent=blog_key())
		content = self.request.get('content')
		
		# if post doesn't exist
		if not self.post_exists(post_id):
			self.render_error(post_id)
		# only logged in users can add comments
		elif not self.user:
			self.redirect('/login')
		elif content:
			comment = Comment(
				parent=Post.get_by_id(int(post_id), parent=blog_key()),
				content=content,
				author=self.user,
				commentId=int(post_id)
				)

			comment.put()
			self.redirect('/post/%s' % post_id)
		else:
			title = 'Add Comment'
			error = 'Please enter some content'

			self.render(
				'comment.html', 
				post_id = post_id,
				title=title, 
				content=content, 
				error=error, 
				addcomment=True
				)
