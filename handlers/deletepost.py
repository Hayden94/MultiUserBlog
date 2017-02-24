from main import Handler, blog_key
from models.post import Post


class DeletePost(Handler):
	def get(self, post_id):
		post = Post.get_by_id(int(post_id), parent=blog_key())

		# if post doesn't exist
		if not self.post_exists(post_id):
			self.render_error(post_id)
		# only logged in users can delete posts
		elif not self.user:
			self.redirect('/login')
		# if the user is not the author of the post
		elif not self.user_owns_post(post_id):
			error = 'You cannot delete another user\'s post'
			link_src = '/post/' + post_id
			link_name = 'Back'

			self.render(
				'information.html',
				error=error,
				link_src=link_src,
				link_name=link_name
				)
		# if the user is the author of the post
		else:
			title = 'Post'
			message = 'Are you sure you want to delete this post?'

			self.render(
				'delete.html',
				post=post,
				post_id=post_id,
				title=title,
				message=message,
				subject=post.subject,
				content=post.content,
				deletepost=True
				)

	def post(self, post_id):
		post = Post.get_by_id(int(post_id), parent=blog_key())

		# if post doesn't exist
		if not self.post_exists(post_id):
			self.render_error(post_id)
		# only logged in users can delete posts
		elif not self.user:
			self.redirect('/login')
		# if the user is the author of the post
		elif self.user_owns_post(post_id):
			post.delete()
			message = 'Your post has been deleted'
			link_src = '/'
			link_name = 'Home'

			self.render(
				'information.html',
				message=message,
				link_src=link_src,
				link_name=link_name
				)
