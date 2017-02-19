import random
import hmac
import string
import hashlib
import re

from secure import *

SECRET = 'strike1298'

def make_secure_val(s):
	return "%s|%s" % (s, hmac.new(SECRET, s).hexdigest())

def check_secure_val(h):
	val = h.split('|')[0]
	if h == make_secure_val(val):
		return val

def make_salt(length = 5):
	return ''.join(random.choice(letters) for x in xrange(length))

def make_pw_hash(name, pw, salt = None):
	if not salt:
		salt = make_salt()
	h = hashlib.sha256(name + pw + salt).hexdigest()
	return '%s,%s' % (salt, h)

def valid_pw(name, password, h):
	salt = h.split(',')[0]
	return h == make_pw_hash(name, password, salt)