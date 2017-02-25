from main import Handler, blog_key
from models.post import Post
from models.likes import Likes


class LikePost(Handler):
    def post(self, post_id):
        post = Post.get_by_id(int(post_id), parent=blog_key())

        # make sure the post exists
        if not self.post_exists(post_id):
            self.render_error(post_id)
        # if user logged in
        elif not self.user:     
            self.redirect('/login')
        # users cannot like their own posts
        elif self.user_owns_post(post_id):
            error = 'You cannot like your own posts'
            link_src = '/post/' + post_id
            link_name = 'Back'

            self.render(
                'information.html',
                post_id=post_id,
                error=error,
                link_src=link_src,
                link_name=link_name
                )
        # like post and put into db
        else:           
            user_id = self.user.key().id()

            l = Likes.all().ancestor(post).filter('user =', user_id).get()
            if l:
                l.delete()

                post.value -= 1
                post.put()
            else:
                like = Likes(
                    parent=post,
                    user=user_id,
                    haveliked=True
                    )
                like.put()

                if like.haveliked is True:
                    post.value += 1

                post.put()

            self.redirect('/post/%s' % post_id)
