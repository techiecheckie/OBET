from flask import current_app, request, url_for
from flask.ext.mongoengine.wtf import model_form
from flask.ext.wtf import Form
from wtforms import StringField, SubmitField
from wtforms.validators import Required
from werkzeug.security import generate_password_hash, check_password_hash
from flask.ext.login import UserMixin, AnonymousUserMixin
import datetime


from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from flask import current_app
from . import db

class UserEditRecord(db.EmbeddedDocument):
    litEdited = db.StringField(required = True)
    litEditedTitle = db.StringField(required = True)
    date = db.DateTimeField(default = datetime.datetime.now, required = True)
    operation = db.StringField(max_length = 30)

    def __repr__(self):
        return '<UserEditRecord %s, %s>' % (self.litEdited, self.date)
    
class LitEditRecord(db.EmbeddedDocument):
	lastUserEdited = db.StringField(max_length = 30, required = True)
	date = db.DateTimeField(default = datetime.datetime.now, required = True)

        def __repr__(self):
            return '<ListEditRecord %s, %s>' % (self.lastUserEdited, self.date)

class User(UserMixin, db.Document):
    	name = db.StringField(max_length = 30, required = True, unique = True)
    	credentials = db.StringField(max_length = 64)
    	email = db.EmailField(min_length = 3, max_length = 30, required = True, unique = True)
    	password_hash = db.StringField(max_length = 120)
    	location = db.StringField(max_length = 64)
    	site = db.URLField(max_length = 200, default = None)
    	description = db.StringField(max_length = 500) #, required = True)
    	confirmed = db.BooleanField(default = False)
    	activated = db.BooleanField(default = True)
    	approved = db.BooleanField(default = False)
    	role = db.ReferenceField('Role')
    	member_since = db.DateTimeField(default = datetime.datetime.now)
 	last_seen = db.DateTimeField(default = datetime.datetime.now)
 	u_edit_record = db.ListField(db.EmbeddedDocumentField(UserEditRecord), default = [])
    	# meta = {'indexes': [
    	# 	{'fields': ['$email', '$name'],
    	# 	 'default_language': 'english',
    	# 	 'weight': {'email': 100, 'name': 50}
    	# 	}
    	# ]}
     
        		
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


	def activate(self):
 		if self.activated:
 			return True
 		self.activated = True
 		self.save()
 		return True
   
	def deactivate(self):
 		if not self.activated:
 			return False
 		self.activated = False
 		self.save()
 		return False

	def approve(self):
 		if not self.approved:
 			return True
 		self.approved = True
 		self.save()
 		return True	
	
 		
	def ping(self):
 		self.last_seen = datetime.datetime.utcnow()
 		self.save()
 		
	def __init__(self, **kwargs):
 		super(User, self).__init__(**kwargs)
 		#self.password = password(self, password)
 		if self.role is None:
 			if self.email == current_app.config['OBET_ADMIN']:
 				self.role = Role.objects(name__iexact = 'Administrator').first()
 				self.confirmed = True
 				self.approved = True
 				self.activated = True
 			else:
 				self.role = Role.objects(name__iexact = 'User').first()
 		if self.confirmed:
 			if self.approved is None:
 				self.approved = True
 			if self.activated is None:
 				self.activated = True
 			if self.member_since is None:
 				self.member_since = datetime.datetime.utcnow

 	
 	def can(self, permissions):
 		return self.role is not None and (self.role.permissions & permissions) == permissions

	def is_administrator(self):
		return self.can(Permission.ADMINISTER)
		

	def generate_reset_token(self, expiration=3600):
		s = Serializer(current_app.config['SECRET_KEY'], expiration)
		return s.dumps({'reset': self.email})

	def reset_password(self, token, new_password):
		s = Serializer(current_app.config['SECRET_KEY'])
		try:
			data = s.loads(token)
		except:
			return False
		if data.get('reset') != self.email:
			return False
		self.password = new_password
		self.save()
		return True


	def generate_email_change_token(self, new_email, expiration=3600):
		s = Serializer(current_app.config['SECRET_KEY'], expiration)
		return s.dumps({'change_email': self.email, 'new_email': new_email})

	def change_email(self, token):
		s = Serializer(current_app.config['SECRET_KEY'])
		try:
			data = s.loads(token)
		except:
			return False
		if data.get('change_email') != self.email:
			return False
		new_email = data.get('new_email')
		if new_email is None:
			return False
		if User.objects(email__iexact = new_email).first() is not None:
			return False
		self.email = new_email
		self.save()
		return True


class AnonymousUser(AnonymousUserMixin):
 	def can(self, permissions):
 		return False
 	
 	def is_administrator(self):
 		return False

REFTYPES = ('Book Section', 'Edited Book', 'Journal Article', 'Journal Issue', 'Magazine Article', 'Media',
    'Newspaper Article', 'Report', 'Thesis', 'Website' )

FIELDS = (('Philosophy/Ethics/Theology','Philosophy/Ethics/Theology'),
            ('Anthropology/Psychology/Sociology','Anthropology/Psychology/Sociology'),
            ('History/Politics/Law','History/Politics/Law'),
            ('Agriculture/Energy/Industry','Agriculture/Energy/Industry'),
            ('Animal Science/Welfare','Animal Science/Welfare'),
            ('Ecology/Conservation','Ecology/Conservation'),
            ('Nature Writing/Art/Literary Criticism','Nature Writing/Art/Literary Criticism'),
            ('Education/Living','Education/Living'))

class Lit(db.Document):
    	refType = db.StringField(max_length = 30, required=True, choices=REFTYPES)
        primaryField = db.StringField(required=True, choices=FIELDS)
        secondaryField = db.StringField(choices=FIELDS)
    	title = db.StringField(max_length = 120, required = True, unique = True)
    	author = db.StringField(max_length = 30, unique_with = ['title'])
    	description = db.StringField(max_length = 500, required = True)
    	edition = db.IntField(default = None)
    	pages = db.StringField(default = None)
    	yrPublished = db.IntField(min_value = 1800, default = None) # MUST ADD max_value!!! Limit it to THIS year!!
    	tags = db.ListField(StringField(max_length = 30), default = [])
    	link = db.URLField(max_length = 200, default = None)
    	l_edit_record = db.ListField(db.EmbeddedDocumentField(LitEditRecord), default = [])
        last_edit = db.EmbeddedDocumentField(LitEditRecord)
        creator = db.StringField(max_length = 30, required = True)
    	# meta = {
     #        'indexes': [
    	# 	  {
     #          'fields': ['$title', '$author', "$description"],
    	# 	  'default_language': 'english',
    	# 	  'weight': {'title': 100, 'author': 50, 'description': 10}
    	# 	  }
    	# ]}

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
