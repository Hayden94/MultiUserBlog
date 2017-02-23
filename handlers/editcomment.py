from main import Handler, blog_key
from models.post import Post
from models.comment import Comment

class EditComment(Handler):
	def get(self, post_id, comment_id):
		post = Post.get_by_id(int(post_id), parent = blog_key())
		comment = Comment.get_by_id(int(comment_id), parent = post)

		# if post exists
		if not self.post_exists(post_id):
			self.render_error(post_id)
		# Only logged in users may delete comments
		elif not self.user:
			self.redirect('/login')
		# if user is not the author of the comment
		elif not self.user_owns_comment(post_id, comment_id):
			error = 'You cannot edit another user\'s comment'
			link_src = '/post/%s' % post_id
			link_name = 'Back'

			self.render('information.html', error = error, link_src = link_src, link_name = link_name)  
		# if user is the author of the comment
		else:
			title = 'Edit Comment'
			content = comment.content

			self.render('comment.html', title = title, content = content, post_id = post_id, addcomment = False, edit = True)
	def post(self, post_id, comment_id):
		post = Post.get_by_id(int(post_id), parent = blog_key())
		comment = Comment.get_by_id(int(comment_id), parent = post)
		content = self.request.get('content')
		
		# if post exists
		if not self.post_exists(post_id):
			self.render_error(post_id)
		# Only logged in users may delete comments
		elif not self.user:
			self.redirect('/login')
		# if content has value
		elif content:
			c = Comment.get_by_id(int(comment_id), parent = post)
			c.content = content
			c.put()
			self.redirect('/post/%s' % post_id)
		# if content has no value
		else:
			title = 'Edit Comment'
			error = 'Please enter some content'

			self.render('comment.html', title = title, content = content, post_id = post_id, error = error, addcoment = False, edit = True)