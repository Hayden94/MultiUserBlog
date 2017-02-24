from main import Handler, blog_key
from models.post import Post
from models.comment import Comment


class DeleteComment(Handler):
	def get(self, post_id, comment_id):
		post = Post.get_by_id(int(post_id), parent=blog_key())
		comment = Comment.get_by_id(int(comment_id), parent=post)

		# if comment exists
		if not self.post_exists(post_id):
			self.render_error(post_id)
		# Only logged in users may delete comments
		elif not self.user:
			self.redirect('/login')
		# if user is not the author of the comment      
		elif not self.user_owns_comment(post_id, comment_id):
			error = 'You cannot delete another user\'s comment'
			link_src = '/post/%s' % post_id
			link_name = 'Back'

			self.render(
				'information.html',
				error=error,
				link_src=link_src,
				link_name=link_name
				)  
		# if user is the author of the comment      
		else:
			title = 'Comment'
			message = 'Are you sure you want to delete this comment?'
			content = comment.content

			self.render(
				'delete.html',
				post_id=post_id,
				title=title,
				message=message,
				content=content, 
				deletepost=False
				)

	def post(self, post_id, comment_id):
		post = Post.get_by_id(int(post_id), parent=blog_key())
		comment = Comment.get_by_id(int(comment_id), parent=post)

		# if post exists
		if not self.post_exists(post_id):
			self.render_error(post_id)
		# Only logged in users may delete comments
		elif not self.user:
			self.redirect('/login')
		# if user is not the author of the comment      
		elif not self.user_owns_comment(post_id, comment_id):
			title = 'Delete Comment'
			error = 'You cannot delete another user\'s comment'
			link_src = '/post/%s' % post_id
			link_name = 'Back'

			self.render(
				'information.html',
				title=title,
				error=error,
				link_src=link_src,
				link_name=link_name
				)
		else:
			comment.delete()

			message = 'Your comment has been deleted'
			link_src = '/post/' + post_id
			link_name = 'Back'

			self.render(
				'information.html',
				message=message,
				post_id=post_id,
				link_src=link_src,
				link_name=link_name
				)
