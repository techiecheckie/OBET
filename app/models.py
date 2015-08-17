from flask import current_app, request, url_for
from flask.ext.mongoengine.wtf import model_form
from flask.ext.wtf import Form
from wtforms import StringField, SubmitField
from wtforms.validators import Required
from werkzeug.security import generate_password_hash, check_password_hash
from flask.ext.login import UserMixin, AnonymousUserMixin


from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from flask import current_app
from . import db

class User(UserMixin, db.Document):
    	name = db.StringField(max_length = 30, required = True, unique = True)
    	credentials = db.StringField(max_length = 8)
    	email = db.EmailField(min_length = 3, max_length = 30, required = True, unique = True)
    	password_hash = db.StringField(max_length = 120)
    	site = db.URLField(max_length = 200, default = None)
    	description = db.StringField(max_length = 500) #, required = True)
    	confirmed = db.BooleanField(default = False)
    	activated = db.BooleanField(default = True)
    	role = db.ReferenceField('Role')
    	#member_since = db.DateTimeField(default = datetime.utcnow)
 	#last_seen = db.DateTimeField(default = datetime.utcnow)
    	meta = {'indexes': [
    		{'fields': ['$email', '$name'],
    		 'default_language': 'english',
    		 'weight': {'email': 100, 'name': 50}
    		}
    	]}
    	#u_edit_record = ListField(EmbeddedDocumentField(UserEditRecord), default = [])
        		
    	def __repr__(self):
 		return '<User %s, %s>' % (self.name, self.email)
 	
 	def is_authenticated(self):
        	return True

    	def is_active(self):
        	return True

    	def is_anonymous(self):
        	return False

    	def get_id(self):
        	return unicode(self.email)
 	
 	@property
 	def password(self):
 		raise AttributeError('password is not a readable attribute')

 	@password.setter
 	def password(self, password):
 		self.password_hash = generate_password_hash(password)
 
 	def verify_password(self, password):
 		return check_password_hash(self.password_hash, password)
 		
 	def generate_confirmation_token(self, expiration=3600):
 		s = Serializer(current_app.config['SECRET_KEY'], expiration)
 		return s.dumps({'confirm': self.name})
 
 	def confirm(self, token):
 		s = Serializer(current_app.config['SECRET_KEY'])
 		try:
 			data = s.loads(token)
 		except:
 			return False
 		if data.get('confirm') != self.name:
 			return False
 		self.confirmed = True
 		self.save()
 		return True
 	
 	### Reactivate when DB objects are updated.
 	#def activate(self):
 	#	if self.activated:
 	#		self.activated = False
 	#	else:
 	#		self.activated = True
 	#	self.save()
 	#	return True
 	
 	#def ping(self):
 	#	self.last_seen = datetime.utcnow()
 	#	self.save()

	def __init__(self, **kwargs):
 		super(User, self).__init__(**kwargs)
 		if self.role is None:
 			if self.email == current_app.config['OBET_ADMIN']:
 				self.role = Role.objects(permissions = 0xff).first()
 			if self.role is None:
 				self.role = Role.objects(default = True).first()
 	
 	def can(self, permissions):
 		return self.role is not None and (self.role.permissions & permissions) == permissions

	def is_administrator(self):
		return self.can(Permission.ADMINISTER)
		

class AnonymousUser(AnonymousUserMixin):
 	def can(self, permissions):
 		return False
 	
 	def is_administrator(self):
 		return False


class Lit(db.Document):
    	refType = db.StringField(max_length = 30, required = True)
    	title = db.StringField(max_length = 120, required = True, unique = True)
    	author = db.StringField(max_length = 30, required = True, unique_with = ['title'])
    	description = db.StringField(max_length = 500, required = True)
    	edition = db.IntField(default = None)
    	pages = db.StringField(default = None)
    	yrPublished = db.IntField(min_value = 1800, default = None) # MUST ADD max_value!!! Limit it to THIS year!!
    	tags = db.ListField(StringField(max_length = 30), default = [])
    	link = db.URLField(max_length = 200, default = None)
    	meta = {'indexes': [
    		{'fields': ['$title', '$author', "$description"],
    		 'default_language': 'english',
    		 'weight': {'title': 100, 'author': 50, 'description': 10}
    		}
    	]}
    	#l_edit_record = ListField(EmbeddedDocumentField(LitEditRecord), default = [])

    	def __repr__(self):
 		return '<Lit %s, %s>' % (self.title, self.author)


class Permission:
	ADDLIT = 0x01
	ADMINISTER = 0x80
 	
class Role(db.Document):
 	name = db.StringField(unique=True)
 	default = db.BooleanField(default = False)
 	permissions = db.IntField()
 	user = db.ReferenceField('User')
 	
 	def __repr__(self):
 		return '<Role %r>' % self.name

	@staticmethod
    	def insert_roles():
        	roles = {
            		'User': (Permission.ADDLIT, True),
            		'Administrator': (0xff, False)
        	}
        	for r in roles:
            		role = Role.objects(name__iexact = 'User').first()
            		if role is None:
                		role = Role(name = r)
            		role.permissions = roles[r][0]
            		role.default = roles[r][1]
            		role.save()

from . import login_manager

login_manager.anonymous_user = AnonymousUser

@login_manager.user_loader
def load_user(user_id):
	u = User.objects(email__iexact = user_id).first()
    	if u is None:
        	return None
    	return u
