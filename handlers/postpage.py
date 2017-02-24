from main import Handler, blog_key
from models.post import Post
from models.comment import Comment
from models.likes import Likes


class PostPage(Handler):
	def get(self, post_id):
		post = Post.get_by_id(int(post_id), parent=blog_key())
		comments = Comment.all().ancestor(post)

		# make sure the post exists
		if not self.post_exists(post_id):
			self.render_error(post_id)
		# only logged in users may like posts
		elif self.user:
			user_id = self.user.key().id()

			# users can only like/dislike the post once
			if Likes.all().ancestor(post).filter('user =', user_id).get():
				status = u"\U0001F44E"
			else:
				status = u"\U0001F44D"
			self.render(
				'post.html',
				post=post,
				value=post.value,
				post_id=post_id,
				status=status, 
				comments=comments
				)
		else:
			status = u"\U0001F44D"
			self.render(
				'post.html',
				post=post,
				value=post.value,
				post_id=post_id,
				status=status,
				comments=comments
				)
