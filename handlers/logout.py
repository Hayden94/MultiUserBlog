from main import Handler


class Logout(Handler):
	def get(self):
		self.logout()
		self.redirect('/')