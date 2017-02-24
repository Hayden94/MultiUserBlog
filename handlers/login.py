from main import Handler
from models.user import User


class Login(Handler):
	def get(self):
		self.render('login.html')
	
	def post(self):
		username = self.request.get('username')
		password = self.request.get('password')

		u = User.login(username, password)
		if u:
			self.login(u)
			self.redirect('/')
		else:
			error = 'Invalid Username or password'
			self.render(
				'login.html',
				error=error
				)
