from main import Handler


class Information(Handler):
    def get(self):
        if not self.user:
            self.redirect('/login')
        else:
            error = 'You have reached this page at an error'
            link_src = '/'
            link_name = 'Home'

            self.render(
                'information.html',
                error=error,
                link_src=link_src,
                link_name=link_name
                )
